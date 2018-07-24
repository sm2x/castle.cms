from castle.cms.behaviors.search import ISearch
from castle.cms.social import COUNT_ANNOTATION_KEY
from collective.elasticsearch import mapping
from collective.elasticsearch import query
from collective.elasticsearch.interfaces import IAdditionalIndexDataProvider
from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements


class MappingAdapter(mapping.MappingAdapter):
    _default_mapping = mapping.MappingAdapter._default_mapping.copy()
    _default_mapping.update({
        'page_views': {'store': True, 'type': 'integer', 'null_value': 0},
        'facebook_shares': {'store': True, 'type': 'integer', 'null_value': 0},
        'twitter_shares': {'store': True, 'type': 'integer', 'null_value': 0},
        'linkedin_shares': {'store': True, 'type': 'integer', 'null_value': 0},
        'pinterest_shares': {'store': True, 'type': 'integer',
                             'null_value': 0},
        'searchterm_pins': {'store': True, 'type': 'text',
                            'index': False},
        'contributors': {'store': False, 'type': 'text',
                         'index': True},
        'immediate_folder': {'store': True, 'type': 'text',
                             'index': False},
        'parent_folder': {'store': True, 'type': 'keyword',
                          'index': False}
    })


class AdditionalIndexDataProvider(object):
    implements(IAdditionalIndexDataProvider)

    def __init__(self, obj):
        self.obj = obj

    def __call__(self, es, existing_data):
        annotations = IAnnotations(self.obj)
        data = {}
        counts = annotations.get(COUNT_ANNOTATION_KEY, {})
        for key, value in counts.items():
            key = key.replace('_matomo', '')
            if isinstance(value, dict):
                value = value.get('total') or 0
            if key in ('page_views',):
                data[key] = value
            else:
                data[key + '_shares'] = value
        sdata = ISearch(self.obj, None)
        if sdata:
            data['searchterm_pins'] = [
                t.lower() for t in sdata.searchterm_pins or [] if t]
        else:
            data['searchterm_pins'] = []

        try:
            data['SearchableText'] = u'%s %s' % (
                existing_data.get('SearchableText', ''),
                u' '.join(data['searchterm_pins']))
        except UnicodeError:
            pass

        try:
<<<<<<< HEAD
            data['contributors'] = list(
                self.obj.creators + self.obj.contributors)
=======
            data['contributors'] = list(self.obj.creators + self.obj.contributors)
>>>>>>> Replace 'string' with 'text' in _default_mapping
        except Exception:
            pass
        path = self.obj.getPhysicalPath()
        data['parent_folder'] = '/'.join(path[:-1])
        site_path = api.portal.get().getPhysicalPath()
        if len(path) > (len(site_path) + 1):
            data['immediate_folder'] = path[len(site_path):][0]
        else:
            data['immediate_folder'] = '/'
        return data


class QueryAssembler(query.QueryAssembler):
    def __call__(self, dquery):
        dquery['trashed'] = False
        query = super(QueryAssembler, self).__call__(dquery)
        # take into account views, likes and custom weighting
        try:
            searchq = dquery.get('SearchableText', '')
            if isinstance(searchq, dict):
                searchq = searchq.get('query', '')
            searchq = searchq.lower().strip('*')
            query = {
                'function_score': {
                    'query': query,
                    # "boost_mode": "sum",  # add score and modified score,
                    'script_score': {
                        'script': {
                            'lang': 'painless',
                            'source': '''int max_shares = 5000;
                                         int max_popularity = 200000;
                                         String[] socialFields = new String[4];
                                         socialFields[0] = 'twitter';
                                         socialFields[1] = 'facebook';
                                         socialFields[2] = 'pinterest';
                                         socialFields[3] = 'linkedin';

                                         float boost = 1.0f;
                                         float max_boost = 2.5f;
                                         long shareCount = 0;

                                         for (int i=0; i<socialFields.length; i++) {
                                            String key = socialFields[i] + '_shares';
                                            if(doc.containsKey(key)){
                                                long docValue = doc[key].value;
                                                shareCount += docValue;
                                            }
                                         }

                                         boost += (shareCount / max_shares);
                                         if (doc.containsKey('page_views')) {
                                           long docValue = doc['page_views'].value;
                                           boost += (docValue / max_popularity);
                                         }
                                         boost = (float)Math.min(boost, max_boost);
                                         return boost;'''
                        }
                    }
                }
            }
        except KeyError:
            pass
        return query
