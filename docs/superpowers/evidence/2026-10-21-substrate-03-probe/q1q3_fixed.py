import json
from probe_lib import PROV, ETKL
VIEW_QUERY_FIXED = json.dumps({"where": [
    ["union",
     [{"@id": "?$identity", PROV + "actedOnBehalfOf": {"@id": "?principal"}},
      {"@id": "?principal", ETKL + "hasRole": {"@id": "?role"}}],
     [{"@id": "?$identity", ETKL + "hasRole": {"@id": "?role"}}]],
    {"@id": "?role", ETKL + "grantsTag": {"@id": "?tag"}},
    {"@id": "?$this", ETKL + "sensitivity": {"@id": "?tag"}}]})

