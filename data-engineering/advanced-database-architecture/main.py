import subprocess
import sys

def run_script(script_name):
    print(f"--- Starting: {script_name} ---")
    try:
        # 'check=True' ensures the main script stops if a sub-script fails
        subprocess.run([sys.executable, script_name], check=True)
        print(f"--- Finished: {script_name} successfully ---\n")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}: {e}")
        sys.exit(1)  # Stop the entire pipeline if a step fails

if __name__ == "__main__":
    # Defining sequence (ignoring notebooks and .js files)
    scripts_to_run = [
        "step1_process_metadata.py",
        "step2_process_transcripts.py",
        "step3_database_loading.py",
        "step4_sql_optimization.py",
        "step6_sql_nosql_merge_and_visualization.py"
    ]

    for script in scripts_to_run:
        run_script(script)
    
    print("Pipeline complete!")