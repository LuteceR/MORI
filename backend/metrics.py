from sqlalchemy import func, select, and_, desc
from fastapi import HTTPException, status, Response
import numpy as np
import json

from models import models, datasets, metrics, metrics_labels, metrics_results
from db import database

async def storeMetricResult(value: float, metric_name: str, metric_id: int):
    """
        Записывает значение одной метрики
    """
    query = metrics_labels.select().where(metrics_labels.c.name == metric_name)
    label = await database.fetch_one(query)

    if label is None:
        add_metric_label = metrics_labels.insert().values([{"name": metric_name}])
        await database.execute(add_metric_label)
        label = await database.fetch_one(query)
    
    query = metrics_results.insert().values(id_metrics_labels=label.id_metrics_labels, id_metrics=metric_id, value=value)
    await database.execute(query)


async def storeResults(results, project_id, dataset_id, model_id):
    """
        Основная функция сохранения метрик.
        Записывает результаты от всех метрик в БД
    """
    details_json = json.dumps({"error_lines": results["error_lines"], "per_label_accuracy": results["per_label_accuracy"]})
    query = metrics.insert().values(id_projects=project_id, id_datasets=dataset_id,
                                id_models=model_id, date=func.current_timestamp(), details=details_json)
    metric_id = (await database.fetch_one(query)).id_metrics

    for metric in results.keys():
        if metric in ["error_lines", "per_label_accuracy"]: continue
        await storeMetricResult(results[metric], metric, metric_id)
    

async def deleteResults(project_id, metric_id):
    """
        Удаление результата запуска модели
    """
    query = metrics.delete().where(
        metrics.c.id_metrics == metric_id and metrics.c.id_projects == project_id
    )
    result = await database.fetch_one(query)
    if not result is None:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Metric (run result) was not found"
            )


async def calcMetrics(data_true, data_pred, text_key, ner_key, labels_names):
    total = 0
    error = 0.0
    errorLines = []
    all_true = np.concatenate([true_label[ner_key] for true_label in data_true])
    all_pred = np.concatenate([pred_label["ner"] for pred_label in data_pred])

    label_correct = {label: 0 for label in labels_names}
    label_total = {label: 0 for label in labels_names}

    for true_item, pred_item in zip(data_true, data_pred):
        true_ner = true_item[ner_key]
        pred_ner = pred_item["ner"]

        n = min(len(true_ner), len(pred_ner))
        total += n
        for i in range(n):
            label_total[true_ner[i]] += 1
            if true_ner[i] == pred_ner[i]:
                label_correct[true_ner[i]] += 1
            else:
                error += 1
                if len(errorLines) < 10:
                    errorLines.append({
                        "word_id": i, 
                        "words": true_item[text_key],
                        "true_labels": true_ner,
                        "pred_labels": pred_ner
                    })
    accuracy_total = (1 - error / total) if total > 0 else 0.0

    label_to_idx = {label: idx for idx, label in enumerate(labels_names)}
    true_indices = [label_to_idx[l] for l in all_true]
    pred_indices = [label_to_idx[l] for l in all_pred]

    cm = np.zeros((len(labels_names), len(labels_names)), dtype=int)
    np.add.at(cm, (true_indices, pred_indices), 1)

    tp = np.trace(cm)
    fp = np.sum(cm, axis=0) - np.diag(cm)
    fn = np.sum(cm, axis=1) - np.diag(cm)

    micro_precision = tp / (tp + np.sum(fp)) if (tp + np.sum(fp)) > 0 else 0.0
    micro_recall = tp / (tp + np.sum(fn)) if (tp + np.sum(fn)) > 0 else 0.0
    micro_f1 = (2 * micro_precision * micro_recall) / (micro_precision + micro_recall) if (micro_precision + micro_recall) > 0 else 0.0

    per_label_accuracy = {}
    for label in labels_names:
        if label_total[label] > 0:
            per_label_accuracy[label] = label_correct[label] / label_total[label]
        else:
            per_label_accuracy[label] = 0.0

    result = {
        "accuracy": accuracy_total,
        "precision": micro_precision,
        "recall": micro_recall,
        "f1-score": micro_f1,
        "total_errors": error,
        "total_objects": total,
        "error_lines": errorLines,
        "per_label_accuracy": per_label_accuracy,
    }
    return result


async def getMetrics(project_id):
    # Доп информация с замеров
    query = (
        select(metrics.c.id_metrics, models.c.name, datasets.c.name, metrics.c.date)
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




async def getMetricsDetails(metric_id):
    query = (
        select(models.c.name, datasets.c.name, metrics.c.date, metrics.c.details)
        .join(models, metrics.c.id_models == models.c.id_models)
        .join(datasets, metrics.c.id_datasets == datasets.c.id_datasets)
        .where(metrics.c.id_metrics == metric_id)
    )
    data = dict(await database.fetch_one(query))
    details = json.loads(data["details"])
    data.pop('details', None)
    return data | details