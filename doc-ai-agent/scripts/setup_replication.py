from dotenv import load_dotenv
import psycopg2
import os
VM_DATABASE_URL = os.getenv("VM_DATABASE_URL")
LOCAL_PUBLIC_URL = os.getenv("LOCAL_PUBLIC_URL")
load_dotenv()

def setup_vm_replication():
    print(f"Connecting to VM Database: {VM_DATABASE_URL} ...")
    
    if LOCAL_PUBLIC_URL is None or "<YOUR_TAILSCALE_HOST>" in LOCAL_PUBLIC_URL:
        print(" WARNING: You need to set LOCAL_PUBLIC_URL in this script!")
        return

    try:
        conn = psycopg2.connect(VM_DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print(f"Creating logical replication subscription from VM to local database...")
        subscription_query = f"""
        CREATE SUBSCRIPTION rag_subscription
        CONNECTION '{LOCAL_PUBLIC_URL}'
        PUBLICATION rag_publication
        WITH (copy_data = false);
        """
        
        try:
            cursor.execute(subscription_query)
            print("Subscription successfully created!")
            print("Data is now syncing in real-time. Only NEW changes will be replicated.")
        except Exception as e:
            if "already exists" in str(e):
                print("Subscription already exists. You can drop it with `DROP SUBSCRIPTION rag_subscription;` if needed.")
            else:
                print(f"Error creating subscription: {e}")
        
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Failed to connect or execute on VM database: {e}")

if __name__ == "__main__":
    setup_vm_replication()
