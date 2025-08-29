#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\dataset_routes.py
# JUMLAH BARIS : 67
#######################################################################

from .base_api_route import BaseApiRoute
class DatasetRoutes(BaseApiRoute):
    """
    Manages API routes for dataset CRUD operations.
    """
    def register_routes(self):
        return {
            "GET /api/v1/datasets": self.handle_get_datasets,
            "POST /api/v1/datasets": self.handle_post_datasets,
            "GET /api/v1/datasets/{dataset_name}/data": self.handle_get_dataset_data,
            "POST /api/v1/datasets/{dataset_name}/data": self.handle_post_dataset_data,
            "DELETE /api/v1/datasets/{dataset_name}": self.handle_delete_dataset, # (ADDED) New route for deletion
        }
    def handle_get_datasets(self, handler):
        dataset_manager = self.service_instance.dataset_manager_service
        if not dataset_manager:
            return handler._send_response(503, {"error": "DatasetManagerService is not available."})
        datasets = dataset_manager.list_datasets()
        handler._send_response(200, datasets)
    def handle_post_datasets(self, handler):
        dataset_manager = self.service_instance.dataset_manager_service
        if not dataset_manager:
            return handler._send_response(503, {"error": "DatasetManagerService is not available."})
        body = handler._get_json_body()
        if not body or 'name' not in body:
            return handler._send_response(400, {"error": "Request body must contain 'name' for the new dataset."})
        success = dataset_manager.create_dataset(body['name'])
        if success:
            handler._send_response(201, {"status": "success", "message": f"Dataset '{body['name']}' created."})
        else:
            handler._send_response(409, {"error": f"Dataset '{body['name']}' already exists or could not be created."})
    def handle_get_dataset_data(self, handler, dataset_name=None):
        dataset_manager = self.service_instance.dataset_manager_service
        if not dataset_manager:
            return handler._send_response(503, {"error": "DatasetManagerService is not available."})
        data = dataset_manager.get_dataset_data(dataset_name)
        handler._send_response(200, data)
    def handle_post_dataset_data(self, handler, dataset_name=None):
        dataset_manager = self.service_instance.dataset_manager_service
        if not dataset_manager:
            return handler._send_response(503, {"error": "DatasetManagerService is not available."})
        body = handler._get_json_body()
        if not body or 'data' not in body or not isinstance(body['data'], list):
            return handler._send_response(400, {"error": "Request body must contain a 'data' list of prompt/response objects."})
        success = dataset_manager.add_data_to_dataset(dataset_name, body['data'])
        if success:
            handler._send_response(200, {"status": "success", "message": f"Added {len(body['data'])} records to dataset '{dataset_name}'."})
        else:
            handler._send_response(500, {"error": f"Failed to add data to dataset '{dataset_name}'."})
    def handle_delete_dataset(self, handler, dataset_name=None):
        dataset_manager = self.service_instance.dataset_manager_service
        if not dataset_manager:
            return handler._send_response(503, {"error": "DatasetManagerService is not available."})
        if not dataset_name:
            return handler._send_response(400, {"error": "Dataset name is required for deletion."})
        success = dataset_manager.delete_dataset(dataset_name)
        if success:
            handler._send_response(204, None) # 204 No Content is standard for successful deletion
        else:
            handler._send_response(404, {"error": f"Dataset '{dataset_name}' not found."})
