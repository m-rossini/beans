from beans.population import SoftLogPopulationEstimator

params_list = [
    dict(width=0, height=100, sprite_size=5, population_density=1.0, male_female_ratio=1.0),
    dict(width=100, height=100, sprite_size=5, population_density=0.0, male_female_ratio=1.0),
    dict(width=100, height=100, sprite_size=1000, population_density=0.0001, male_female_ratio=1.0),
]

def raw_capacity(params: dict) -> tuple[float, int]:
    area = params['width'] * params['height']
    per_bean_area = max(1, params['sprite_size'] ** 2)
    raw_total = area * params['population_density'] / per_bean_area
    return raw_total, int(raw_total)

estimator = SoftLogPopulationEstimator()
for params in params_list:
    raw, capped = raw_capacity(params)
    try:
        male, female = estimator.estimate(**params)
        print(
            "params", params, 
            "raw", raw, "capped", capped,
            "output", male + female
        )
    except Exception as exc:
        print(
            "params", params,
            "raw", raw, "capped", capped,
            "exception", type(exc).__name__, exc
        )
