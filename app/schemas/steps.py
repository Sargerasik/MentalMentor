# app/schemas/steps.py
from __future__ import annotations
from pydantic import BaseModel, Field, conint, constr
from typing import Literal, Union, Optional

# ---- CONFIGS ----
class StepConfigBase(BaseModel):
    pass

class MeditationConfig(StepConfigBase):
    _type: Literal["meditation"] = "meditation"
    duration_min: conint(ge=1, le=180) = 10  # минуты

class ReadingConfig(StepConfigBase):
    _type: Literal["reading"] = "reading"
    start_page: conint(ge=1)
    end_page: conint(ge=1)
    # опционально — ключ PDF, если не общий для курса
    storage_key: Optional[str] = None

class QuizConfig(StepConfigBase):
    _type: Literal["quiz"] = "quiz"
    questions_key: constr(min_length=1)  # ключ к вопросам (отдельная таблица/хранилище)

class ReflectionConfig(StepConfigBase):
    _type: Literal["reflection"] = "reflection"
    prompt: constr(min_length=1)

class VideoConfig(StepConfigBase):
    _type: Literal["video"] = "video"
    url: constr(min_length=1)
    duration_sec: conint(ge=1)

class ExerciseConfig(StepConfigBase):
    _type: Literal["exercise"] = "exercise"
    reps: conint(ge=1) | None = None
    duration_sec: conint(ge=1) | None = None

StepConfig = Union[MeditationConfig, ReadingConfig, QuizConfig, ReflectionConfig, VideoConfig, ExerciseConfig]

# ---- METRICS (на комплишн) ----
class MetricsBase(BaseModel): pass

class MeditationMetrics(MetricsBase):
    _type: Literal["meditation"] = "meditation"
    actual_duration_sec: conint(ge=0)

class ReadingMetrics(MetricsBase):
    _type: Literal["reading"] = "reading"
    pages_read: conint(ge=0)

class QuizMetrics(MetricsBase):
    _type: Literal["quiz"] = "quiz"
    correct: conint(ge=0)
    total: conint(ge=0)

class ReflectionMetrics(MetricsBase):
    _type: Literal["reflection"] = "reflection"
    notebook_entry_id: int

class VideoMetrics(MetricsBase):
    _type: Literal["video"] = "video"
    watched_sec: conint(ge=0)

class ExerciseMetrics(MetricsBase):
    _type: Literal["exercise"] = "exercise"
    done_reps: conint(ge=0) | None = None
    done_duration_sec: conint(ge=0) | None = None

StepMetrics = Union[MeditationMetrics, ReadingMetrics, QuizMetrics, ReflectionMetrics, VideoMetrics, ExerciseMetrics]

# ---- API DTO ----
class CourseStepCreate(BaseModel):
    title: str = Field(max_length=200)
    order_index: int = Field(ge=0)
    type: Literal["meditation","reading","quiz","reflection","video","exercise"]
    config: StepConfig

class CourseStepRead(BaseModel):
    id: int
    title: str
    order_index: int
    type: str
    config: StepConfig
    class Config: from_attributes = True

class StepCompletePayload(BaseModel):
    metrics: StepMetrics
