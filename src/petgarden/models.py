from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

SPECIES_CHECK = "species IN ('cat','dog','rabbit','panda','fox','dragon')"


class Base(DeclarativeBase):
    pass


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[str] = mapped_column(String(32))


class Class(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))
    grade: Mapped[str | None] = mapped_column(String(30), nullable=True)
    color: Mapped[str] = mapped_column(String(20), default="moss")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[str] = mapped_column(String(32))
    updated_at: Mapped[str] = mapped_column(String(32))


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        CheckConstraint("score BETWEEN 0 AND 100", name="ck_students_score"),
        CheckConstraint(SPECIES_CHECK, name="ck_students_species"),
        CheckConstraint("is_present IN (0, 1)", name="ck_students_present"),
        Index("idx_students_class_score", "class_id", "score"),
        Index("idx_students_class_seat", "class_id", "seat_no"),
        Index(
            "uq_students_class_no",
            "class_id",
            "student_no",
            unique=True,
            sqlite_where=text("student_no IS NOT NULL AND student_no <> ''"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(20))
    student_no: Mapped[str | None] = mapped_column(String(20), nullable=True)
    seat_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0)
    species: Mapped[str] = mapped_column(String(10))
    is_present: Mapped[int] = mapped_column(Integer, default=1)
    last_picked_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32))
    updated_at: Mapped[str] = mapped_column(String(32))


class PetProgress(Base):
    __tablename__ = "pet_progress"
    __table_args__ = (
        CheckConstraint("best_level BETWEEN 1 AND 5", name="ck_progress_best"),
        CheckConstraint(SPECIES_CHECK, name="ck_progress_species"),
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    )
    species: Mapped[str] = mapped_column(String(10), primary_key=True)
    best_level: Mapped[int] = mapped_column(Integer, default=1)
    first_reached_at: Mapped[str] = mapped_column(String(32))
    last_reached_at: Mapped[str] = mapped_column(String(32))


class ScoreEvent(Base):
    __tablename__ = "score_events"
    __table_args__ = (
        CheckConstraint("delta BETWEEN -5 AND 5 AND delta <> 0", name="ck_events_delta"),
        CheckConstraint("score_before BETWEEN 0 AND 100", name="ck_events_before"),
        CheckConstraint("score_after BETWEEN 0 AND 100", name="ck_events_after"),
        Index("idx_events_class_id", "class_id", text("id DESC")),
        Index("idx_events_student_id", "student_id", text("id DESC")),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id", ondelete="CASCADE"))
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"))
    delta: Mapped[int] = mapped_column(Integer)
    score_before: Mapped[int] = mapped_column(Integer)
    score_after: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str | None] = mapped_column(String(60), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32))
    undone_at: Mapped[str | None] = mapped_column(String(32), nullable=True)