from ekg_simulator.ekg_simulator import EKGSimulator

if __name__ == "__main__":
    """
    Entry point for the EKG Simulator application.
    """
    print("Starting EKG Simulator...")
    simulator = EKGSimulator()
    
    # Configure simulation parameters if needed, e.g.:
    # simulator.sampling_rate = 100 # Hz
    # simulator.plotter.display_seconds = 10 # seconds
    # simulator.simulation_time_step_seconds = 0.1 # seconds, how often new data is generated
    
    # To demonstrate a specific starting condition, you could uncomment the following:
    # simulator.set_blood_volume_percentage(85) # Start in Class II shock
    
    try:
        simulator.run_simulation()
    except Exception as e:
        print(f"An error occurred during simulation: {e}")
        # Add any specific cleanup or error handling here
    finally:
        print("EKG Simulator finished or was interrupted.")

# To run this simulator, you might need to install dependencies:
# pip install numpy matplotlib neurokit2
#
# If you encounter issues with Matplotlib backends, especially on servers
# or environments without a display, you might need to install a backend like TkAgg:
# sudo apt-get update
# sudo apt-get install python3-tk
#
# Or, for other environments, you might need to configure Matplotlib
# to use a different backend (e.g., 'Qt5Agg', 'Agg' for non-GUI).
# This can sometimes be done by setting the MPLBACKEND environment variable
# or by using matplotlib.use('BackendName') before importing pyplot.
# However, for a real-time plot, a GUI-capable backend is necessary.
