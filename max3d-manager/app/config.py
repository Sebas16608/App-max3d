import json
import os


class Config:
    def __init__(self):
        self.config_dir = os.path.join(os.path.expanduser("~"), ".config", "max3d-manager")
        self.config_file = os.path.join(self.config_dir, "settings.json")
        self.db_path = os.path.join(self.config_dir, "max3d.db")
        os.makedirs(self.config_dir, exist_ok=True)

        self.defaults = {
            "modelado_costo_hora": 25.0,
            "desgaste_costo_hora": 0.75,
            "electricidad_costo": 0.000153,
            "electricidad_potencia": 300,
            "trabajo_porcentaje": 20.0,
            "redondeo": 5,
            "moneda": "Q",
        }

        self.data = {}
        self.load()

    def load(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    self.data = json.load(f)
            else:
                self.data = dict(self.defaults)
                self.save()
        except:
            self.data = dict(self.defaults)
            self.save()

    def save(self):
        with open(self.config_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def get(self, key, default=None):
        return self.data.get(key, self.defaults.get(key, default))

    def set(self, key, value):
        self.data[key] = value
        self.save()
