import duckdb

class DuckDBConnector:
    # Connect to the database
    # singleton pattern
    _instance = None
    def __init__(self) -> None:
        self.connect()

    @staticmethod
    def get_instance():
        if DuckDBConnector._instance is None:
            DuckDBConnector._instance = DuckDBConnector()
        return DuckDBConnector._instance
    
    def connect(self):
        self.cursor = duckdb.connect()

    def calculate_zone_group(self, zone):
        if zone == 'ALL':
            return zone
        
        zone = int(zone)
        ZONE_GROUPS = [ (x, x+20) for x in range(0, 800, 20) ]
        for group in ZONE_GROUPS:
            if zone >= group[0] and zone < group[1]:
                return f"{group[0]}-{group[1]}"

    def get_vote_time_metrics(self, uf, turno, zone, section):
        table = """
            read_parquet(
                '/src/VOTES_TIME_METRICS.parquet/*/*/*/*.parquet', 
                hive_partitioning=True,
                hive_types_autocast=0
            )
        """
        zone_group = self.calculate_zone_group(zone)
        zone = F"{int(zone):04d}" if zone != 'ALL' else zone
        section = F"{int(section):04d}" if section != 'ALL' else section

        if uf == 'ALL':
            uf = "','".join([
                "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
                "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
                "SP", "SE", "TO", "ZZ", "ALL"
            ])
            
        query = f"""
            SELECT *
            FROM {table}
            WHERE 1=1
            AND turno = '{turno}'
            AND uf in ('{uf}')
            AND zone_group = '{zone_group}'
            AND zone_code = '{zone}'
            AND section_code = '{section}'
        """

        data = self.cursor.execute(query).df()
        return data