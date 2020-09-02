# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from skipchunk.sq import SkipchunkQuery

from flask import Blueprint, redirect, render_template
from flask import request, url_for, jsonify
from flask_user import current_user, login_required, roles_required

from app import db
from app.models.user_models import UserProfileForm


q = SkipchunkQuery('http://localhost:8983/solr/','bii-connectivity-and-tech')

main_blueprint = Blueprint('main', __name__, template_folder='templates')

# The Home page is accessible to anyone
@main_blueprint.route('/')
def home_page():
    return render_template('main/home_page.html')

# Suggest is our AJAX call for typeahead
@main_blueprint.route('/suggest')
def suggest():
    prefix = request.args["query"]
    suggestions = q.suggestConcepts(prefix)
    return jsonify({'suggestions':suggestions})

# Cores is our AJAX call for core lists
@main_blueprint.route('/cores')
def cores():
    cores = q.cores()
    return jsonify({'cores':cores})

@main_blueprint.route('/cores/<name>',methods=['POST'])
def core_change(name):
    success = q.changeCore(name)
    if success:
        return jsonify({'message':'Core changed to'+name}), 200
    return jsonify({'message':'Core'+name+'not found'}), 404

@main_blueprint.route('/cores/<name>',methods=['GET'])
def core(name):
    concepts,predicates = q.summarize()
    return jsonify({'concepts':concepts,'predicates':predicates}), 200

@main_blueprint.route('/graph',methods=['GET'])
def graph():
    subject = request.args["subject"]
    if "objects" in request.args.keys():
        objects = int(request.args["objects"])
    else:
        objects = 5
    if "branches" in request.args.keys():
        branches = int(request.args["branches"])
    else:
        branches = 10
    tree = q.graph(subject,objects=objects,branches=branches)
    return jsonify(tree), 200

@main_blueprint.route('/explore2',methods=['GET'])
def explore2():
    prefix = request.args["query"]
    tree = q.explore(prefix,quiet=True)
    concept = list(tree.keys())[0]
    verb = tree[concept][0]["label"]

    return jsonify(q.conceptVerbConcepts(concept,verb)), 200


# The User page is accessible to authenticated users (users that have logged in)
@main_blueprint.route('/member')
@login_required  # Limits access to authenticated users
def member_page():
    return render_template('main/user_page.html')


# The Admin page is accessible to users with the 'admin' role
@main_blueprint.route('/admin')
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_page():
    return render_template('main/admin_page.html')


@main_blueprint.route('/main/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    # Initialize form
    form = UserProfileForm(request.form, obj=current_user)

    # Process valid POST
    if request.method == 'POST' and form.validate():
        # Copy form fields to user_profile fields
        form.populate_obj(current_user)

        # Save user_profile
        db.session.commit()

        # Redirect to home page
        return redirect(url_for('main.home_page'))

    # Process GET or invalid POST
    return render_template('main/user_profile_page.html',
                           form=form)


