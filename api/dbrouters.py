# api/dbrouters.py
class SeqMapRouter:
    """
    A router for directing database operations for the 'seqmap' app.

    Args:
        model (type): The model class to check for database routing.
        db (str): The database name to check for migration permissions.
        app_label (str): The label of the app requesting migration.

    Returns:
        str or None: The database name for read/write operations or None if not applicable.

    """

    def db_for_read(self, model, **hints):
        """
        Determine the database alias for reading based on model attributes.

            Args:
                model (Type[Model]): The model class to check for database routing.
                **hints: Additional hints for database routing.

            Returns:
                Optional[str]: The database alias if applicable, otherwise None.

        """
        return "seqmap" if getattr(model, "seqmap_db", False) else None

    def db_for_write(self, model, **hints):
        """
        Determines the database for write operations, which is read-only.

        Args:
            model (Type): The model class to check.
            **hints: Additional hints for database routing.

        Returns:
            None: Indicates that write operations are not allowed.

        """
        return None  # read-only

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Prevent migrations for the 'seqmap' app and prevent any app
        from migrating to the 'seqmap' database.
        """
        if app_label == "seqmap":
            return False
        if db == "seqmap":
            return False
        return None
