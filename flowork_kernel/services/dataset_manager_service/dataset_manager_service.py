#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\dataset_manager_service\dataset_manager_service.py
# JUMLAH BARIS : 61
#######################################################################

import os
import threading
import json
from ..base_service import BaseService
class DatasetManagerService(BaseService):
    """
    (REFACTORED) Manages CRUD operations for fine-tuning datasets.
    This service was previously misnamed as DatabaseService.
    """
    DB_NAME = "datasets.json"
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.db_path = os.path.join(self.kernel.data_path, self.DB_NAME)
        self.lock = threading.Lock()
    def _read_db(self):
        with self.lock:
            if not os.path.exists(self.db_path):
                return {}
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
    def _write_db(self, data):
        with self.lock:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
    def list_datasets(self):
        db = self._read_db()
        return [{"name": name} for name in db.keys()]
    def get_dataset_data(self, dataset_name: str):
        db = self._read_db()
        return db.get(dataset_name, [])
    def create_dataset(self, name: str):
        db = self._read_db()
        if name in db:
            return False  # Already exists
        db[name] = []
        self._write_db(db)
        return True
    def add_data_to_dataset(self, dataset_name: str, data_list: list):
        db = self._read_db()
        if dataset_name not in db:
            return False # Dataset does not exist
        db[dataset_name].extend(data_list)
        self._write_db(db)
        return True
    def delete_dataset(self, name: str):
        db = self._read_db()
        if name in db:
            del db[name]
            self._write_db(db)
            return True # Deletion successful
        return False # Dataset not found
