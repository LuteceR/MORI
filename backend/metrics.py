from sqlalchemy import func, select, and_, desc
from models import models, datasets, metrics, metrics_labels, metrics_results
from fastapi import HTTPException, status, Response
from db import database


async def createCommonMetricsLabels():
    """
        DEV-функция для создания низваний базовых метрик
    """
    labels = ["accuracy", "total_errors", "total_objects"]
    rows = [{"name": label} for label in labels]
    query = metrics_labels.insert().values(rows)
    return await database.execute(query)


async def storeMetricResult(value: float, metric_name: str, metric_id: int):
    """
        Записывает значение одной метрики
    """
    query = metrics_labels.select().where(metrics_labels.c.name == metric_name)
    label = await database.fetch_one(query)

    if label is None:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
                                    detail = f"Invalid metric's name: {metric_name}")
    
    query = metrics_results.insert().values(id_metrics_labels=label.id_metrics_labels, id_metrics=metric_id, value=value)
    await database.execute(query)


async def storeResults(results, project_id, dataset_id, model_id):
    """
        Основная функция.
        Записывает результаты от всех метрик в БД
    """
    query = metrics.insert().values(id_projects=project_id, id_datasets=dataset_id,
                                id_models=model_id, date=func.current_timestamp(), details=str(results["error_lines"]))
    metric_id = (await database.fetch_one(query)).id_metrics

    for metric in ["accuracy", "total_errors", "total_objects"]:
        await storeMetricResult(results[metric], metric, metric_id)
    

async def calcMetrics(data_true, data_pred, text_key):
    total = 0
    error = 0.0
    errorLines = []

    for true_item, pred_item in zip(data_true, data_pred):
        true_ner = true_item['ner']
        pred_ner = pred_item['ner']

        n = min(len(true_ner), len(pred_ner))
        total += n
        for i in range(n):
            if true_ner[i] != pred_ner[i]:
                error += 1
                if len(errorLines) < 10:
                    errorLines.append({"word_id": i, 
                                        "words": true_item[text_key],
                                        "true_labels": true_ner,
                                        "pred_labels": pred_ner
                                        })
    accuracy = (1 - error / total) if total > 0 else 0.0
    result = {
        "accuracy": accuracy,
        "total_errors": error,
        "total_objects": total,
        "error_lines": errorLines
    }
    return result


async def getMetrics(project_id):
    # Доп информация с замеров
    query = (
        select(metrics.c.id_metrics, models.c.name, datasets.c.name, metrics.c.date, metrics.c.details)
        .join(models, metrics.c.id_models == models.c.id_models)
        .join(datasets, metrics.c.id_datasets == datasets.c.id_datasets)
        .where(metrics.c.id_projects == project_id)
        .order_by(desc(metrics.c.date))
    )
    data = await database.fetch_all(query)

    if data is None or len(data) == 0:
        return []
    result = list(map(dict, data))

    # Значения метрик + их названия
    for i, metric_id in enumerate(list(map(lambda row: row.id_metrics, data))):
        query = (
            select(metrics_results.c.value, metrics_labels.c.name)
            .join(metrics_labels, metrics_results.c.id_metrics_labels == metrics_labels.c.id_metrics_labels)
            .where(metrics_results.c.id_metrics == metric_id)
        )
        metrics_data = await database.fetch_all(query)
        result[i]["metrics_data"] = metrics_data
    return result

