# Original work: Copyright 2014 SolidBuilds.com. All rights reserved
# Authors: Ling Thio <ling.thio@gmail.com>

# Modified work: Copyright 2020 OpenSourceConnections.com.  All rights reserved
# Authors: Max Irwin <mirwin@opensourceconnections.com>

from skipchunk.graphquery import GraphQuery
from skipchunk.indexquery import IndexQuery
from skipchunk.enrichquery import EnrichQuery

from flask import Blueprint, redirect, render_template
from flask import request, url_for, jsonify
from flask_user import current_user, login_required, roles_required

from app import db
from app.models.user_models import UserProfileForm

from ..local_settings import ENGINE_CONFIG

eq = EnrichQuery(model='en_core_web_lg')
iq = IndexQuery(ENGINE_CONFIG,enrich_query=eq)
gq = GraphQuery(ENGINE_CONFIG)

graph_connections = {}
index_connections = {}

def graph_connect(name):
    if name not in graph_connections.keys():
        graph_config = ENGINE_CONFIG.copy()
        graph_config["name"] = name
        graph_connections[name] = GraphQuery(graph_config)
    return graph_connections[name]

def index_connect(name):
    if name not in index_connections.keys():
        index_config = ENGINE_CONFIG.copy()
        index_config["name"] = name
        index_connections[name] = IndexQuery(index_config,enrich_query=eq)
    return index_connections[name]

main_blueprint = Blueprint('main', __name__, template_folder='templates')

# The Home page is accessible to anyone
@main_blueprint.route('/')
def home_page():
    return render_template('main/home_page.html')

# Suggest is our AJAX call for typeahead
@main_blueprint.route('/suggest/<name>')
def suggest(name):
    prefix = request.args["query"]
    suggestions = gq.suggestConcepts(prefix)
    return jsonify({'suggestions':suggestions})

# Cores is our AJAX call for core lists
@main_blueprint.route('/indexes')
def indexes():
    indexes = gq.indexes()
    return jsonify({'indexes':indexes})

@main_blueprint.route('/indexes/<name>',methods=['GET'])
def index_summarize(name):
    gq = graph_connect(name)
    concepts,predicates = gq.summarize()
    return jsonify({'concepts':concepts,'predicates':predicates}), 200

@main_blueprint.route('/search/<name>',methods=['GET'])
def search(name):
    iq = index_connect(name)
    query = request.args.copy()
    results,status = iq.search(query)
    return results,status

@main_blueprint.route('/graph/<name>',methods=['GET'])
def graph(name):
    gq = graph_connect(name)
    subject = request.args["subject"]
    if "objects" in request.args.keys():
        objects = int(request.args["objects"])
    else:
        objects = 5
    if "branches" in request.args.keys():
        branches = int(request.args["branches"])
    else:
        branches = 10
    tree = gq.graph(subject,objects=objects,branches=branches)
    return jsonify(tree), 200

@main_blueprint.route('/explore/<name>',methods=['GET'])
def explore(name):
    gq = graph_connect(name)
    prefix = request.args["query"]
    tree = gq.explore(prefix,quiet=True)
    concept = list(tree.keys())[0]
    verb = tree[concept][0]["label"]

    return jsonify(gq.conceptVerbConcepts(concept,verb)), 200


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
    return render_template('main/user_profile_page.html', form=form)