import json


def build_model_contract(blueprint):

    contract = {}

    models = blueprint.get(
        "models",
        {}
    )

    for model_name, model_info in models.items():

        contract[model_name] = {
            "fields": model_info.get(
                "fields",
                {}
            )
        }

    return contract