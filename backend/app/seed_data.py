import os
import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load env directly here so this script can be run standalone
load_dotenv()
COGNODB_URI = os.getenv("COGNODB_URI")
COGNODB_PASSWORD = os.getenv("COGNODB_PASSWORD")
COGNODB_USER = "cognodb"

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "investments_VC.csv")

def clear_db(session):
    print("Clearing existing data...")
    session.run("MATCH (n) DETACH DELETE n")

def create_constraints(session):
    print("Creating constraints...")
    # Add IF NOT EXISTS for neo4j 5+ compatibility
    queries = [
        "CREATE CONSTRAINT company_name IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE",
        "CREATE CONSTRAINT investor_name IF NOT EXISTS FOR (i:Investor) REQUIRE i.name IS UNIQUE",
        "CREATE CONSTRAINT market_name IF NOT EXISTS FOR (m:Market) REQUIRE m.name IS UNIQUE",
        "CREATE CONSTRAINT region_name IF NOT EXISTS FOR (r:Region) REQUIRE r.name IS UNIQUE"
    ]
    for q in queries:
        try:
            session.run(q)
        except Exception as e:
            print(f"Warning on constraint: {e}")

def seed_synthetic_data(session):
    print("No CSV found. Seeding synthetic dataset...")
    
    # 1. Create Companies
    companies = [
        {"name": "TechCorp", "category": "Software", "status": "operating", "founded_year": 2018},
        {"name": "AICo", "category": "Artificial Intelligence", "status": "acquired", "founded_year": 2020},
        {"name": "CloudNet", "category": "Cloud Computing", "status": "ipo", "founded_year": 2015}
    ]
    session.execute_write(lambda tx: tx.run(
        "UNWIND $companies AS c "
        "MERGE (comp:Company {name: c.name}) "
        "SET comp.category = c.category, comp.status = c.status, comp.founded_year = c.founded_year",
        companies=companies
    ))

    # 2. Create Investors
    investors = [{"name": "Sequoia Capital"}, {"name": "John Doe"}, {"name": "Y Combinator"}]
    session.execute_write(lambda tx: tx.run(
        "UNWIND $investors AS i "
        "MERGE (:Investor {name: i.name})",
        investors=investors
    ))

    # 3. Create Markets and Regions
    markets = [{"name": "Software"}, {"name": "Artificial Intelligence"}, {"name": "Cloud Computing"}]
    regions = [{"name": "San Francisco", "country_code": "USA"}, {"name": "London", "country_code": "GBR"}]
    
    session.execute_write(lambda tx: tx.run(
        "UNWIND $markets AS m MERGE (:Market {name: m.name})", markets=markets
    ))
    session.execute_write(lambda tx: tx.run(
        "UNWIND $regions AS r MERGE (reg:Region {name: r.name}) SET reg.country_code = r.country_code", regions=regions
    ))

    # 4. Create Relationships
    investments = [
        {"investor": "Sequoia Capital", "company": "CloudNet", "type": "series_a", "amount": 10000000, "year": 2016},
        {"investor": "Y Combinator", "company": "AICo", "type": "seed", "amount": 120000, "year": 2020},
        {"investor": "John Doe", "company": "TechCorp", "type": "angel", "amount": 50000, "year": 2018}
    ]
    session.execute_write(lambda tx: tx.run(
        "UNWIND $investments AS inv "
        "MATCH (i:Investor {name: inv.investor}) "
        "MATCH (c:Company {name: inv.company}) "
        "MERGE (i)-[r:INVESTED_IN]->(c) "
        "SET r.funding_round_type = inv.type, r.amount_usd = inv.amount, r.year = inv.year",
        investments=investments
    ))

    locations = [
        {"company": "TechCorp", "region": "San Francisco", "market": "Software"},
        {"company": "AICo", "region": "London", "market": "Artificial Intelligence"},
        {"company": "CloudNet", "region": "San Francisco", "market": "Cloud Computing"}
    ]
    session.execute_write(lambda tx: tx.run(
        "UNWIND $locations AS loc "
        "MATCH (c:Company {name: loc.company}) "
        "MATCH (r:Region {name: loc.region}) "
        "MATCH (m:Market {name: loc.market}) "
        "MERGE (c)-[:LOCATED_IN]->(r) "
        "MERGE (c)-[:OPERATES_IN]->(m)",
        locations=locations
    ))

def seed_from_csv(session, csv_path):
    print(f"Found CSV at {csv_path}. Parsing and seeding...")
    df = pd.read_csv(csv_path, encoding='ISO-8859-1', low_memory=False)
    
    # We will limit to 500 rows to ensure fast seeding for the assignment
    df = df.head(500).fillna('Unknown')
    
    top_investors = ["Sequoia Capital", "Y Combinator", "Andreessen Horowitz", "Founders Fund", "Accel", "Benchmark"]
    
    for index, row in df.iterrows():
        company_name = str(row.get('name', 'Unknown'))
        market_name = str(row.get(' market ', 'Unknown')).strip()
        region_name = str(row.get(' region ', 'Unknown')).strip()
        status = str(row.get('status', 'Unknown'))
        
        # The Kaggle CSV doesn't have explicit investor names, so we link a deterministic 
        # "synthetic" investor based on the company name hash so our Graph Schema is fully populated.
        inv_idx = hash(company_name) % len(top_investors)
        investor_name = top_investors[inv_idx]
        
        query = """
        MERGE (c:Company {name: $company_name})
        SET c.status = $status
        
        MERGE (m:Market {name: $market_name})
        MERGE (r:Region {name: $region_name})
        MERGE (i:Investor {name: $investor_name})
        
        MERGE (c)-[:OPERATES_IN]->(m)
        MERGE (c)-[:LOCATED_IN]->(r)
        MERGE (i)-[:INVESTED_IN {funding_round_type: 'venture'}]->(c)
        """
        session.run(query, company_name=company_name, status=status, market_name=market_name, region_name=region_name, investor_name=investor_name)
    
    print("CSV Seeding complete with synthesized investors.")

def main():
    if not COGNODB_URI or not COGNODB_PASSWORD:
        print("COGNODB_URI or COGNODB_PASSWORD not set. Exiting.")
        return

    driver = GraphDatabase.driver(COGNODB_URI, auth=(COGNODB_USER, COGNODB_PASSWORD))
    
    with driver.session() as session:
        clear_db(session)
        create_constraints(session)
        
        if os.path.exists(CSV_PATH):
            seed_from_csv(session, CSV_PATH)
        else:
            seed_synthetic_data(session)
            
    driver.close()
    print("Seeding finished successfully!")

if __name__ == "__main__":
    main()
