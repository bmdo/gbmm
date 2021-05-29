import time
import logging
from server.gb_api import resources


class Controller:
    def __init__(self):
        self.logger = logging.getLogger('gbmm').getChild('controller')

    def get_collection_resource(self, item_name: str):
        return resources.collection_resources.get_resource_by_item_name(item_name)

    def get_most_recent(self, res) -> list:
        self.logger.info(f'Getting latest {res.result_object_definition.collection_name}...')
        start_time = time.time()
        res.filters.set('sort', 'publish_date:desc')
        res.filters.set('offset', 0)
        end_of_new = False
        new_objs = []
        while not end_of_new:
            count = 0
            for r in res.next():
                # TODO
                existing = self.db.objects.get_one(r.guid)
                if existing is None:
                    count += 1
                    # TODO
                    obj = self.db.objects.add(r)
                    if obj is not None:
                        new_objs.append(obj)
            end_of_new = count != res.response_metadata.number_of_page_results
        end_time = time.time()
        self.logger.info(f'Added {len(new_objs)} new {res.result_object_definition.collection_name} in '
                         f'{end_time - start_time} seconds.')
        return new_objs

    def initialize_resource(self, res):
        self.logger.info(f'Initializing all {res.result_object_definition.collection_name}...')
        start_time = time.time()
        res.filters.set('sort', 'publish_date:desc')
        res.filters.set('offset', 0)
        count = 0
        end_of_results = False
        while not end_of_results:
            iter_start_time = time.time()
            for r in res.next():
                # TODO
                self.db.objects.add(r)
            iter_end_time = time.time()
            count += res.response_metadata.number_of_page_results
            self.logger.info(f'Added {res.response_metadata.number_of_page_results} '
                             f'{res.result_object_definition.collection_name} '
                             f'in {iter_end_time - iter_start_time} seconds.')
            results_remaining =\
                res.response_metadata.number_of_total_results -\
                (res.response_metadata.offset + res.response_metadata.limit)
            end_of_results = res.response_metadata.is_last_page
            if not end_of_results:
                self.logger.info(f'Results remaining: {results_remaining}')
                if count * results_remaining > 0:
                    self.logger.info(f'Estimated time remaining: '
                                     f'{(iter_end_time - start_time) / count * results_remaining} seconds')

        end_time = time.time()
        self.logger.info(f'Completed initialization for {res.result_object_definition.collection_name}.')
        self.logger.info(f'Added a total of {count} {res.result_object_definition.collection_name} in'
                         f'{end_time - start_time} seconds.')
