import couchdb
from .proxy import DBProxy


class CouchDBProxy(DBProxy):

    @classmethod
    def build(cls, uri, user=None, password=None, **kwargs):
        conn = couchdb.Server(uri)
        if user and password:
            conn.resource.credentials = (user, password)

        return CouchDBProxy(conn)

    def __init__(self, db):
        self._db = db

    def available_views(self, model):
        class ViewInfo(object):
            def __init__(self, name, reduced, group, view_def):
                self.name = name
                self.reduced = reduced
                self.group = group
                self.view_def = view_def

        viewgroups = self.collection(model).view(name='_all_docs', startkey="_design/", endkey="_design0", include_docs='true')
        views = []
        for view_group in viewgroups:
            group_id = view_group.key.replace('_design/', '')
            for subview_name, subview_def in view_group['doc'].get('views', {}).items():
                view_name = "{}/{}".format(group_id, subview_name)
                views.append(ViewInfo(view_name, True if 'reduce' in subview_def else False, '_design/'+group_id, subview_def))

        return views

    def view(self, model, name, key=None, include_docs=False, limit=None, **kwargs):
        # If looking for a single key/element, then return a single result
        if key or limit == 1:
            if key:
                kwargs['key'] = key

            elif limit == 1:
                kwargs['limit'] = limit

            result = self.collection(model).view(name, include_docs=include_docs, **kwargs)

            if limit == 1:
                result = result.rows[0].doc if result and result.rows else None

        else:
            result = self.collection(model).view(name, include_docs=include_docs, **kwargs)

        return result

    def iterview(self, model, name, batch=5000, startkey=None, start_key_docid=None, endkey=None, end_key_docid=None,
                 keys=None, stale=None, reduce=False, include_docs=False, **kwargs):
        options = kwargs

        if stale:
            options['stale'] = stale

        if keys:
            options['keys'] = keys
        else:
            if startkey:
                options['startkey'] = startkey,
                if start_key_docid:
                    options['startkey_docid'] = start_key_docid,

            if endkey:
                options['endkey'] = endkey,
                if end_key_docid:
                    options['endkey_docid'] = end_key_docid,

        return self.collection(model).iterview(name=name, batch=batch, reduce=reduce, include_docs=include_docs, **options)

    def purge(self, model, docs=None):
        docs = docs or [r.doc for r in self.iterview(model=model, name='_all_docs', include_docs=True) if r.doc]

        for r in docs:
            self.collection(model).delete(r)

    def _get_view_and_keys_from_condition(self, model, condition, sort=None):
        if condition and len(condition) > 1:
            raise Exception("CouchDB filters by matching keys. The condition parameter should be"
                            "the name of a view with the value to look for in the index")

        view, startkey, endkey, keys = None, None, None, None

        if not condition:
            view = '_all_docs'

        else:
            view_name = list(condition.keys())[0]

            sort_field = sort.replace('<', '').replace('>', '') if sort else None

            if sort_field:
                view_name += '_{}'.format('_'.join(sort.split(',')))

            for v in self.available_views(model):
                if view_name in v.name:
                    view = v.name

            if not view:
                raise Exception("CouchDB doesn't have a view with the name '{}'".format(view_name))

            value = list(condition.values())[0]

            if value.get('range'):
                startkey = value[0]
                endkey = value[1]
            else:
                keys = value

        return view, startkey, endkey, keys

    def collection(self, model):
        collection_name = model.collection_name or model.__class__.__name__.lower() + 's'
        return self._db[collection_name]

    def add(self, model, doc):
        self.collection(model).save(doc)

    def upsert(self, model, *docs):
        for d in docs:
            self.collection(model).update(d)

    def delete(self, model, *doc_ids):
        for d in self.iterview(model=model, name='_all_docs', keys=doc_ids, include_docs=True):
            self.collection(model).delete(d.doc)

    def count(self, model, condition, **kwargs):
        view, startkey, endkey, keys = self._get_view_and_keys_from_condition(model, condition)

        params = {
            'name': view,
        }

        if keys:
            params['keys'] = keys
        else:
            params['startkey'] = startkey
            params['endkey'] = endkey

        if view == '_all_docs':
            total = sum([1 for d in self.iterview(model=model, name=view, include_docs=False) if '_design' not in d.id])

        else:
            result = self.view(model=model, reduce=True, include_docs=False, **params, **kwargs)
            total = result.rows[0].value if result else 0

        return total

    def find(self, model, condition, skip=0, limit=0, sort=None, count=False, **kwargs):
        view, startkey, endkey, keys = self._get_view_and_keys_from_condition(model, condition, sort)

        params = {
            'name': view,
        }

        if keys:
            params['keys'] = keys
        else:
            params['startkey'] = startkey
            params['endkey'] = endkey

        if sort and sort.startswith('<'):
            params['descending'] = True

        result = self.iterview(model=model, skip=skip, limit=limit, include_docs=True, **params, **kwargs)

        for d in result:
            yield model.build(d.doc)

    def by_attr(self, model, attr, value, exact=True, many=True, skip=0, limit=0, sort=None):
        # CouchDB doesnt support regex and there's no way of filtering in a soft way
        # meaning, attributes that contain a certain value. It Can only do exact matching
        # or range matching, start/end keys

        results = self.find(model, condition={attr: value}, skip=skip, limit=limit, sort=sort)

        if many:
            for d in results:
                yield model.build(d.doc)
        else:
            yield model.build(results.rows[0].doc if results and results.rows else {})

    def by_id(self, model, id):
        return next(self.by_attr(model, '_id', id, many=False))




