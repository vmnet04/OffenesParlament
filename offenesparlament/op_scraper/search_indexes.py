from haystack import indexes
import datetime

from op_scraper.models import Person, Law, Debate, Inquiry
import json
from haystack import connections

# maintain list of which fields are json-content
JSON_FIELDS = {
    'person': [
        'mandates',
        'statements',
        'debate_statements',
        'inquiries_sent',
        'inquiries_received',
        'inquiries_answered'
    ],
    'law': [
        'steps',
        'opinions',
        'documents'
    ],
}
import logging

# Get an instance of a logger
logger = logging.getLogger('elasticsearch')

def extract_json_fields(result, type):
    for field in JSON_FIELDS[type]:
        try:
            result[field] = json.loads(result[field])
        except:
            # didn't work, maybe not json data after all? anywho, no harm done
            pass
    return result


class BaseIndex(object):
    pass

    # Uncomment the following to limit the amount of objects indexed for
    # debug reasons (it be much faster that way)
    # def build_queryset(self, start_date=None, end_date=None, using=None):
    #     "Only index a random 100 Objects"
    #     return self.get_model().objects.all()[:10]

class ArchiveIndexMixin(object):

    def _get_backend(self, using):
        return connections['archive'].get_backend()

    def reindex(self, using='archive'):
        """
        Completely clear the index for this model and rebuild it.
        Always work on 'archive' index/connection
        """
        self.clear(using='archive')
        self.update(using='archive')

    def build_queryset(self, start_date=None, end_date=None, using=None):
        """
        Override to always retun an empty array. This archive indices should not
        be used via rebuild_index or update_index, they shoud only be accessed
        through the low-level ES api
        """
        return self.get_model().objects.none()

    def index_queryset(self, start_date=None, end_date=None, using=None):
        """
        Override to always retun an empty array. This archive indices should not
        be used via rebuild_index or update_index, they shoud only be accessed
        through the low-level ES api
        """
        return self.get_model().objects.none()


class PersonIndex(BaseIndex, indexes.SearchIndex, indexes.Indexable):
    FIELDSETS = {
        'all': [
            'text',
            'category',
            'ts',
            'parl_id',
            'source_link',
            'internal_link',
            'api_url',
            'photo_link',
            'photo_copyright',
            'birthdate',
            'deathdate',
            'full_name',
            'reversed_name',
            'birthplace',
            'deathplace',
            'occupation',
            'party',
            'llps',
            'llps_numeric',
            'mandates',
            'statements',
            'debate_statements',
            'inquiries_sent',
            'inquiries_received',
            'inquiries_answered',
            'comittee_memberships'
        ],
        'list': [
            'text',
            'category',
            'ts',
            'parl_id',
            'source_link',
            'internal_link',
            'api_url',
            'photo_link',
            'photo_copyright',
            'birthdate',
            'deathdate',
            'full_name',
            'reversed_name',
            'birthplace',
            'deathplace',
            'occupation',
            'party',
            'llps',
            'llps_numeric'
        ],
    }

    text = indexes.CharField(document=True, use_template=True)
    ts = indexes.DateTimeField(model_attr='ts', faceted=True, default=datetime.datetime(1970, 1, 1, 0, 0))
    parl_id = indexes.CharField(model_attr='parl_id')

    source_link = indexes.CharField(model_attr='source_link')
    internal_link = indexes.CharField(model_attr='slug')
    photo_link = indexes.CharField(model_attr='photo_link')
    photo_copyright = indexes.CharField(model_attr='photo_copyright')

    birthdate = indexes.DateTimeField(model_attr='birthdate', null=True)
    deathdate = indexes.DateTimeField(model_attr='deathdate', null=True)
    full_name = indexes.CharField(model_attr='full_name')
    reversed_name = indexes.CharField(model_attr='reversed_name')
    birthplace = indexes.CharField(
        model_attr='birthplace', faceted=True, null=True)
    deathplace = indexes.CharField(
        model_attr='deathplace', faceted=True, null=True)
    occupation = indexes.CharField(
        model_attr='occupation', faceted=True, null=True)
    party = indexes.CharField(model_attr='party', faceted=True, null=True)
    llps = indexes.MultiValueField(model_attr='llps_facet', faceted=True)
    llps_numeric = indexes.MultiValueField(
        model_attr='llps_facet_numeric', faceted=True)

    # Secondary Items
    mandates = indexes.CharField()
    statements = indexes.CharField()
    debate_statements = indexes.CharField()
    inquiries_sent = indexes.CharField()
    inquiries_received = indexes.CharField()
    inquiries_answered = indexes.CharField()
    comittee_memberships = indexes.MultiValueField()

    # Static items
    category = indexes.CharField(faceted=True, null=True)
    api_url = indexes.CharField()

    def prepare_api_url(self, obj):
        return obj.api_slug()

    def prepare_category(self, obj):
        try:
            logger.INFO(u"Indexing {}".format(obj.full_name))
        except:
            # some unicode shit here
            pass
        return "Person"

    def prepare_mandates(self, obj):
        """
        Collects the object's mandates as json
        """
        return obj.mandates_json()

    def prepare_statements(self, obj):
        """
        Collects the object's statements's as json
        """
        return obj.statements_json()

    def prepare_debate_statements(self, obj):
        """
        Collects the object's statements's as json
        """
        return obj.debate_statements_json()

    def prepare_inquiries_sent(self, obj):
        """
        Collects the object's inquiries sent as json
        """
        return obj.inquiries_sent_json()

    def prepare_inquiries_received(self, obj):
        """
        Collects the object's inquiries received as json
        """
        return obj.inquiries_received_json()

    def prepare_inquiries_answered(self, obj):
        """
        Collects the object's inquiries answered as json
        """
        return obj.inquiries_answered_json()

    def prepare_comittee_memberships(self, obj):
        """
        Collects the object's inquiries answered as json
        """
        return [unicode(cm) for cm in obj.comittee_memberships.all()]

    def get_model(self):
        return Person

class LawIndex(BaseIndex, indexes.SearchIndex, indexes.Indexable):

    FIELDSETS = {
        'all': [
            'text',
            'parl_id',
            'ts',
            'internal_link',
            'api_url',
            'title',
            'description',
            'category',
            'llps',
            'llps_numeric',
            'steps',
            'opinions',
            'documents',
            'keywords',
            'response_id',
        ],
        'list': [
            'text',
            'parl_id',
            'ts',
            'internal_link',
            'api_url',
            'title',
            'description',
            'category',
            'llps',
            'llps_numeric',
            'steps',
            'opinions',
            'documents',
            'keywords',
            'response_id',
        ],
    }

    text = indexes.CharField(document=True, use_template=True)
    parl_id = indexes.CharField(model_attr='parl_id')
    source_link = indexes.CharField(model_attr='source_link')
    ts = indexes.DateTimeField(
        model_attr='ts', faceted=True, default=datetime.datetime(1970, 1, 1, 0, 0))

    internal_link = indexes.CharField(model_attr=u'slug')
    api_url = indexes.CharField()

    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description')
    status = indexes.CharField(model_attr='status', null=True)
    category = indexes.CharField(
        model_attr='category__title', faceted=True, null=True)
    llps = indexes.MultiValueField(model_attr='llps_facet', faceted=True)
    llps_numeric = indexes.MultiValueField(
        model_attr='llps_facet_numeric', faceted=True)

    # Related, aggregated and Multi - Value Fields
    'api_url',
    opinions = indexes.CharField()
    documents = indexes.CharField()
    keywords = indexes.MultiValueField(
        model_attr='keyword_titles', faceted=True)
    response_id = indexes.CharField()


    # Use this to limit which (inherited) laws should be scraped
    # The example shows how to remove inquiries/responses from the list
    # def index_queryset(self, using=None):
    #     return self.get_model().objects\
    #         .filter(inquiry__isnull=False)\
    #         .filter(inquiryresponse__isnull=False)

    def prepare_api_url(self, obj):
        return obj.api_slug()

    def prepare_steps(self, obj):
        """
        Collects the object's step's as json
        """
        return obj.steps_and_phases_json()

    def prepare_opinions(self, obj):
        """
        Collects the object's opinions's id
        """
        return obj.opinions_json()

    def prepare_documents(self, obj):
        """
        Collects the object's documents's id
        """
        return obj.documents_json()

    def prepare_response_id(self, obj):
        if hasattr(obj, 'inquiry'):
            r = obj.inquiry.response
            return None if not r else r.pk
        return None

    def get_model(self):
        return Law



class DebateIndex(BaseIndex, indexes.SearchIndex, indexes.Indexable):
    FIELDSETS = {
        'all': [
            'text',
            'parl_id',
            'category',
            'date',
            'title',
            'debate_type',
            'protocol_url',
            'detail_url',
            'nr',
            'llp',
            'statements',
            'internal_link'
        ],
        'list': [
            'parl_id',
            'category',
            'date',
            'title',
            'debate_type',
            'protocol_url',
            'detail_url',
            'nr',
            'llp',
            'internal_link'
        ],
    }

    text = indexes.CharField(document=True, use_template=True)

    parl_id = indexes.CharField(model_attr='parl_id')
    date = indexes.DateTimeField(model_attr='date', faceted=True)
    title = indexes.CharField(model_attr='title')
    debate_type = indexes.CharField(model_attr='debate_type', faceted=True)
    protocol_url = indexes.CharField(model_attr='protocol_url')
    detail_url = indexes.CharField(model_attr='detail_url')
    nr = indexes.IntegerField(model_attr='nr', null=True)
    llps = indexes.MultiValueField(model_attr='llps_facet', faceted=True)
    llps_numeric = indexes.MultiValueField(
        model_attr='llps_facet_numeric', faceted=True)

    # soon
    internal_link = indexes.CharField(model_attr=u'slug')

    # Related, aggregated and Multi - Value Fields
    statements = indexes.MultiValueField()

    # Static items
    category = indexes.CharField(faceted=True, null=True)

    def prepare_category(self, obj):
        try:
            logger.INFO(u"Indexing {}".format(obj.title))
        except:
            # some unicode shit here
            pass
        return "Debatte"

    def prepare_statements(self, obj):
        """
        Collects the object's statements's as json
        """
        return obj.statements_full_text

    def get_model(self):
        return Debate


## Index duplication for Archive
class PersonIndexArchive(ArchiveIndexMixin, PersonIndex):
    pass

class LawIndexArchive(ArchiveIndexMixin, LawIndex):
    pass

class DebateIndexArchive(ArchiveIndexMixin, DebateIndex):
    pass
