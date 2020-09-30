import re

#------------------------------------------

def queryparser(q_param,val):
    #A simple and fast query parser
    #format MUST be:
    # {!hello_nlp f=[FIELDNAME] v=[TEXT|$q] func=[ANALYZER]}

    template = ""
    text = ""
    analyzer = ""

    m = re.search(r'(\{\!hello_nlp)([^\}]+)(\})', val)
    if m and m.groups:
        subquery = str(m.groups(0)[0])
        props = str(m.groups(0)[1]).strip().split(' ')
        endtag = str(m.groups(0)[2])

        for prop in props:
            param = prop.split('=')
            k = param[0]
            v = param[1]                        

            if k=='f':
                template = v
            elif k =='v':
                if v == '$q':
                    v = q_param
                text = v
            elif k in ['analyzer','func']:
                analyzer = v
        
    return template,analyzer,text