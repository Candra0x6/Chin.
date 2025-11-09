"""
Database configuration and connection management.
Handles connection to Supabase PostgreSQL database using psycopg2.
"""

from typing import Optional, Dict, Any, List
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extensions import register_adapter, AsIs
from contextlib import contextmanager
import json
from datetime import datetime
import numpy as np
from app.config import settings


# Custom JSON encoder for numpy types
class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy types"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# Register JSON adapter for dict types
def adapt_dict_to_json(data):
    """Adapt Python dict to PostgreSQL JSON, handling numpy types"""
    json_str = json.dumps(data, cls=NumpyEncoder)
    return AsIs(f"'{json_str}'::jsonb")

register_adapter(dict, adapt_dict_to_json)


class DatabasePool:
    """
    Connection pool manager for PostgreSQL database.
    Provides efficient connection reuse and management.
    """
    
    _pool: Optional[SimpleConnectionPool] = None
    
    @classmethod
    def initialize(cls):
        """Initialize database connection pool."""
        if cls._pool is None:
            try:
                cls._pool = SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    user=settings.db_user,
                    password=settings.db_password,
                    host=settings.db_host,
                    port=settings.db_port,
                    database=settings.db_name,

                )
                print("✅ Database connection pool initialized")
            except Exception as e:
                print(f"❌ Failed to initialize database pool: {e}")
                raise
    
    @classmethod
    def get_connection(cls):
        """Get connection from pool."""
        if cls._pool is None:
            cls.initialize()
        return cls._pool.getconn()
    
    @classmethod
    def return_connection(cls, conn):
        """Return connection to pool."""
        if cls._pool:
            cls._pool.putconn(conn)
    
    @classmethod
    def close_all(cls):
        """Close all connections in pool."""
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Automatically handles connection cleanup.
    
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM table")
    """
    conn = DatabasePool.get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        DatabasePool.return_connection(conn)


class Database:
    """Database operations wrapper compatible with Supabase client API."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self._select_fields = "*"
        self._filters = []
        self._order_by = None
        self._limit_value = None
        self._offset_value = None
        self._count_mode = None  # For count="exact"
    
    def select(self, fields: str = "*", count: str = None):
        """Select fields to retrieve with optional count mode."""
        self._select_fields = fields
        self._count_mode = count
        return self
    
    def eq(self, column: str, value: Any):
        """Add equality filter."""
        self._filters.append((column, "=", value))
        return self
    
    def ilike(self, column: str, pattern: str):
        """Add case-insensitive LIKE filter."""
        self._filters.append((column, "ILIKE", pattern))
        return self
    
    def gte(self, column: str, value: Any):
        """Add greater than or equal filter."""
        self._filters.append((column, ">=", value))
        return self
    
    def gt(self, column: str, value: Any):
        """Add greater than filter."""
        self._filters.append((column, ">", value))
        return self
    
    def lte(self, column: str, value: Any):
        """Add less than or equal filter."""
        self._filters.append((column, "<=", value))
        return self
    
    def lt(self, column: str, value: Any):
        """Add less than filter."""
        self._filters.append((column, "<", value))
        return self
    
    def order(self, column: str, desc: bool = False):
        """Add ordering."""
        direction = "DESC" if desc else "ASC"
        self._order_by = f"{column} {direction}"
        return self
    
    def limit(self, count: int):
        """Set limit."""
        self._limit_value = count
        return self
    
    def range(self, start: int, end: int):
        """Set range (offset and limit)."""
        self._offset_value = start
        self._limit_value = end - start + 1
        return self
    
    def execute(self):
        """Execute the query and return results."""
        params = []
        
        # Handle INSERT
        if hasattr(self, '_pending_insert') and self._pending_insert:
            data = self._pending_insert
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ["%s"] * len(values)
            
            query = f"""
                INSERT INTO {self.table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                RETURNING *
            """
            
            with get_db_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute(query, values)
                result = cursor.fetchone()
                cursor.close()
            
            return type('Response', (), {'data': [dict(result)] if result else []})()
        
        # Handle UPDATE
        if hasattr(self, '_pending_update') and self._pending_update:
            data = self._pending_update
            set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
            params = list(data.values())
            
            query = f"UPDATE {self.table_name} SET {set_clause}"
            
            # Add WHERE clause
            if self._filters:
                conditions = []
                for col, op, val in self._filters:
                    conditions.append(f"{col} {op} %s")
                    params.append(val)
                query += " WHERE " + " AND ".join(conditions)
            
            query += " RETURNING *"
            
            with get_db_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute(query, params)
                results = cursor.fetchall()
                cursor.close()
            
            return type('Response', (), {'data': [dict(row) for row in results]})()
        
        # Handle DELETE
        if hasattr(self, '_pending_delete') and self._pending_delete:
            query = f"DELETE FROM {self.table_name}"
            params = []
            
            # Add WHERE clause
            if self._filters:
                conditions = []
                for col, op, val in self._filters:
                    conditions.append(f"{col} {op} %s")
                    params.append(val)
                query += " WHERE " + " AND ".join(conditions)
            
            query += " RETURNING *"
            
            with get_db_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute(query, params)
                results = cursor.fetchall()
                cursor.close()
            
            return type('Response', (), {'data': [dict(row) for row in results]})()
        
        # Handle SELECT (default)
        query = f"SELECT {self._select_fields} FROM {self.table_name}"
        params = []
        
        # Add WHERE clause
        if self._filters:
            conditions = []
            for col, op, val in self._filters:
                conditions.append(f"{col} {op} %s")
                params.append(val)
            query += " WHERE " + " AND ".join(conditions)
        
        # Add ORDER BY
        if self._order_by:
            query += f" ORDER BY {self._order_by}"
        
        # Add LIMIT and OFFSET
        if self._limit_value:
            query += f" LIMIT {self._limit_value}"
        if self._offset_value:
            query += f" OFFSET {self._offset_value}"
        
        # Execute query
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            data = cursor.fetchall()
            
            # Get count if requested
            count = None
            if self._count_mode == "exact":
                # Build count query (same filters, no limit/offset)
                count_query = f"SELECT COUNT(*) as count FROM {self.table_name}"
                if self._filters:
                    count_conditions = []
                    count_params = []
                    for col, op, val in self._filters:
                        count_conditions.append(f"{col} {op} %s")
                        count_params.append(val)
                    count_query += " WHERE " + " AND ".join(count_conditions)
                
                cursor.execute(count_query, count_params if self._filters else [])
                count_result = cursor.fetchone()
                count = count_result['count'] if count_result else 0
            
            cursor.close()
        
        # Return in Supabase-compatible format with count
        response_obj = {'data': [dict(row) for row in data]}
        if count is not None:
            response_obj['count'] = count
        
        return type('Response', (), response_obj)()
    def insert(self, data: Dict[str, Any]):
        """Insert data into table. Returns self for .execute() chaining."""
        self._pending_insert = data
        return self
    
    def update(self, data: Dict[str, Any]):
        """Update data in table. Returns self for .execute() chaining."""
        self._pending_update = data
        return self
    
    def delete(self):
        """Delete data from table. Returns self for .execute() chaining."""
        self._pending_delete = True
        return self


class SupabaseClient:
    """Supabase-compatible client using psycopg2."""
    
    def table(self, table_name: str) -> Database:
        """Get table accessor."""
        return Database(table_name)


# Singleton instance
_client: Optional[SupabaseClient] = None


def get_supabase() -> SupabaseClient:
    """
    Get database client instance (Supabase-compatible).
    
    Returns:
        SupabaseClient: Database client instance
        
    Example:
        >>> db = get_supabase()
        >>> data = db.table('analysis_results').select('*').execute()
    """
    global _client
    if _client is None:
        DatabasePool.initialize()
        _client = SupabaseClient()
    return _client


# Database table names
class Tables:
    """Database table name constants."""
    
    ANALYSIS_RESULTS = "analysis_results"
    CHAT_HISTORY = "chat_history"
    VIDEO_UPLOADS = "video_uploads"

