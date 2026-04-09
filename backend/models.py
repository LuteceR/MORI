from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, TIMESTAMP

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id_users", Integer, primary_key=True),
    Column("username", String(50), unique=True, nullable=False, index=True),
    Column("password", String, nullable=False),
)

projects = Table(
    "projects",
    metadata,
    Column("id_projects", Integer, primary_key=True),
    Column("name", String(50), nullable=False, index=True),
    Column("description", String),
    Column("id_users", Integer, ForeignKey("users.id_users"), nullable=False)
)

models = Table(
    "models",
    metadata,
    Column("id_models", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("folder_path", String(260), nullable=False),
    Column("id_original_model", Integer, ForeignKey("models.id_models"))
)

projects_models = Table(
    "projects_models",
    metadata,
    Column("id_projects_models", Integer, primary_key=True),
    Column("id_projects", ForeignKey("projects.id_projects"), nullable=False),
    Column("id_models", ForeignKey("models.id_models"), nullable=False)
)

url_sources = Table(
    "url_sources",
    metadata,
    Column("id_url_sources", Integer, primary_key=True),
    Column("id_model", Integer, ForeignKey("models.id_models"), nullable=False),
    Column("url_source", String, nullable=False)
)

datasets = Table(
    "datasets",
    metadata,
    Column("id_datasets", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("url_source", String, nullable=False),
    Column("folder_path", String(260), nullable=False)
)

projects_datasets = Table(
    "projects_datasets",
    metadata,
    Column("id_projects_datasets", Integer, primary_key=True),
    Column("id_projects", Integer, ForeignKey("projects.id_projects"), nullable=False),
    Column("id_datasets", Integer, ForeignKey("datasets.id_datasets"), nullable=False)
)

marks = Table(
    "marks",
    metadata,
    Column("id_marks", Integer, primary_key=True),
    Column("id_datasets", Integer, ForeignKey("datasets.id_datasets"), nullable=False),
    Column("file_path", String(260), nullable=False)
)

metrics = Table(
    "metrics",
    metadata,
    Column("id_metrics", Integer, primary_key=True),
    Column("date", TIMESTAMP, nullable=False),
    Column("id_projects", Integer, ForeignKey("projects.id_projects"), nullable=False),
    Column("id_datasets", Integer, ForeignKey("datasets.id_datasets"), nullable=False),
)

models_snapshots = Table(
    "models_snapshots",
    metadata,
    Column("id_models_snapshots", Integer, primary_key=True),
    Column("id_models", Integer, ForeignKey("models.id_models"), nullable=False),
    Column("id_metrics", Integer, ForeignKey("metrics.id_metrics"), nullable=False),
    Column("params_path", String, nullable=False)
)

datasets_snapshots = Table(
    "datasets_snapshots",
    metadata,
    Column("id_datasets_snapshots", Integer, primary_key=True),
    Column("id_datasets", Integer, ForeignKey("datasets.id_datasets"), nullable=False),
    Column("id_metrics", Integer, ForeignKey("metrics.id_metrics"), nullable=False),
    Column("folder_path", String, nullable=False)
)

marks_snapshots = Table(
    "marks_snapshots",
    metadata,
    Column("id_marks_snapshots", Integer, primary_key=True),
    Column("id_datasets_snapshots", Integer, ForeignKey("datasets_snapshots.id_datasets_snapshots"),nullable=False),
    Column("file_path", String(260), nullable=False)
)

metrics_labels = Table(
    "metrics_labels",
    metadata,
    Column("id_metrics_labels", Integer, primary_key=True),
    Column("name", String(100), nullable=False, unique=True)
)

metrics_results = Table(
    "metrics_results",
    metadata,
    Column("id_metrics_results", Integer, primary_key=True),
    Column("id_metrics_labels", Integer, ForeignKey("metrics_labels.id_metrics_labels"), nullable=False),
    Column("id_metrics", Integer, ForeignKey("metrics.id_metrics"), nullable=False)
)