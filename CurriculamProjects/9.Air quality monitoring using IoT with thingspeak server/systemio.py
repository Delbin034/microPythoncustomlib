# =========================================================
# SYSTEM IO LIBRARY
# Safe Keyboard Interrupt + Cleanup Handler
# =========================================================

import sys

# ---------------------------------------------------------
# SAFE RUN FUNCTION
# ---------------------------------------------------------

def run(main_function, cleanup_function=None):

    try:

        print("Program Started")

        # Run main loop/function
        main_function()

    except KeyboardInterrupt:

        print("\nKeyboard Interrupt Detected")
        print("Stopping Program Safely...")

        # Run cleanup function if available
        if cleanup_function is not None:

            try:
                cleanup_function()

            except Exception as error:
                print("Cleanup Error:", error)

        print("Program Stopped Safely")

    except Exception as error:

        print("Runtime Error:", error)

        # Cleanup on normal errors too
        if cleanup_function is not None:

            try:
                cleanup_function()

            except:
                pass

    finally:

        print("System Exit")

