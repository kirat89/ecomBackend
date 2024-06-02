import logging
import asyncpg
from typing import List, Dict, Any, Tuple, Union, Optional

class AsyncExecutor:
    """AsyncExecutor Class to Execute queries asynchronously."""

    def __init__(self, conn: asyncpg.Connection):
        """Constructor for class where connection is a required argument."""
        self.conn = conn
        self.err: Optional[str] = None
        self.lastrowid: int = -1
        self.rowcount: int = -1
        self.trans: Optional[asyncpg.transaction.Transaction] = None
        self.resultcount: int = -1

    def _get_dict_res(self, rec_res: List[asyncpg.Record]) -> List[Dict[str, Any]]:
        """Converts records objects to dict."""
        return [dict(rec) for rec in rec_res]

    async def _get_res_data(self, quer: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """To execute select statement."""
        params = params or ()
        res = await self.conn.fetch(quer, *params)
        return_data = self._get_dict_res(res)
        self.resultcount = len(return_data)
        return return_data

    async def _insert_data(self, quer: str, params: Optional[Tuple] = None) -> None:
        """To execute insert statement."""
        params = params or ()
        self.lastrowid = await self.conn.fetchval(quer, *params)

    async def _execute_quer(self, quer: str, params: Optional[Tuple] = None) -> None:
        """To execute delete and update statements."""
        params = params or ()
        res = await self.conn.execute(quer, *params)
        self.rowcount = int(res.split(" ")[-1])

    async def begin_trans(self) -> None:
        """Will begin transaction."""
        self.trans = self.conn.transaction()
        await self.trans.start()

    async def commit(self) -> None:
        """Will commit transaction."""
        if self.trans:
            await self.trans.commit()

    async def rollback(self) -> None:
        """Will rollback transaction."""
        if self.trans:
            await self._trans.rollback()

    # Advisory Lock Methods
    async def acquire_advisory_lock(self, lock_key: int) -> None:
        """Acquire an advisory lock."""
        await self.conn.execute("SELECT pg_advisory_lock($1)", lock_key)

    async def release_advisory_lock(self, lock_key: int) -> None:
        """Release an advisory lock."""
        await self.conn.execute("SELECT pg_advisory_unlock($1)", lock_key)

    # Pessimistic Lock Methods
    async def _get_res_data_with_lock(self, quer: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """To execute select statement with a pessimistic lock."""
        params = params or ()
        res = await self.conn.fetch(f"{quer} FOR UPDATE", *params)
        return_data = self._get_dict_res(res)
        self.resultcount = len(return_data)
        return return_data

    async def execute_query(
        self, quer: str, params: Optional[Tuple] = None, begin_trans: bool = True, complete_trans: bool = True,
        advisory_lock_key: Optional[int] = None, use_pessimistic_lock: bool = False
    ) -> Union[List[Dict[str, Any]], None]:
        """
        Execute a query with optional transaction and locking management.

        Select statement executes without transaction by default, and other DML statements with transaction.
        Advisory and pessimistic locks can also be used.
        """
        queryval = quer.upper().strip()
        if advisory_lock_key is not None:
            await self.acquire_advisory_lock(advisory_lock_key)
        
        try:
            if queryval.startswith("SELECT") or queryval.startswith("WITH"):
                if use_pessimistic_lock:
                    return await self._get_res_data_with_lock(quer, params)
                else:
                    return await self._get_res_data(quer, params)
            elif queryval.startswith("INSERT"):
                if begin_trans:
                    await self.begin_trans()
                try:
                    await self._insert_data(quer, params)
                    if complete_trans:
                        await self.commit()
                except Exception as err:
                    if begin_trans:
                        await self.rollback()
                    self.err = str(err)
                    logging.error(err)
                    raise
            elif queryval.startswith("UPDATE") or queryval.startswith("DELETE"):
                if begin_trans:
                    await self.begin_trans()
                try:
                    await self._execute_quer(quer, params)
                    if complete_trans:
                        await self.commit()
                except Exception as exe:
                    if begin_trans:
                        await self.rollback()
                    self.err = str(exe)
                    logging.error(exe)
                    raise
        finally:
            if advisory_lock_key is not None:
                await self.release_advisory_lock(advisory_lock_key)

    async def prepare_and_execute_query(
        self, quer: str, params: List[Tuple], begin_trans: bool = True, complete_trans: bool = True,
        advisory_lock_key: Optional[int] = None
    ) -> Tuple[List[Any], List[Tuple]]:
        """
        Execute a prepared query with multiple parameters and optional advisory lock.

        If query is select, this function will return a list of resultsets.
        If query is insert, will return a list of row ids provided the query has a returning id statement.
        If update or delete, will return a list of row counts for each param.
        """
        queryval = quer.upper().strip()
        stmt = await self.conn.prepare(quer)
        res = []
        err = []

        if advisory_lock_key is not None:
            await self.acquire_advisory_lock(advisory_lock_key)

        try:
            if queryval.startswith("SELECT"):
                for param in params:
                    temp_res = await stmt.fetch(*param)
                    res.append(self._get_dict_res(temp_res))
                return res, err
            if queryval.startswith("INSERT"):
                if begin_trans:
                    await self.begin_trans()
                for param in params:
                    try:
                        res.append(await stmt.fetchval(*param))
                    except Exception as exe:
                        if begin_trans:
                            await self.rollback()
                        res.append(None)
                        err.append(param)
                        logging.error(f"Error with param {param}: {exe}")
                        raise Exception(f"{str(exe)} error with param {str(param)}") from exe
                if complete_trans:
                    await self.commit()
            elif queryval.startswith("UPDATE") or queryval.startswith("DELETE"):
                if begin_trans:
                    await self.begin_trans()
                for param in params:
                    try:
                        await stmt.fetch(*param)
                        tempres = stmt.get_statusmsg()
                        res.append(int(tempres.split(" ")[-1]))
                    except Exception as exe:
                        if begin_trans:
                            await self.rollback()
                        res.append(None)
                        err.append(param)
                        logging.error(f"Error with param {param}: {exe}")
                        raise Exception(f"{str(exe)} error with param {str(param)}") from exe
                if complete_trans:
                    await self.commit()
        finally:
            if advisory_lock_key is not None:
                await self.release_advisory_lock(advisory_lock_key)

        return res, err
