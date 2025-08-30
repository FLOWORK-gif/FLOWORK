# [MODIFICATION] Commented out the problematic circular import.
# The Kernel class should be imported directly from its file (e.g., from flowork_kernel.kernel import Kernel)
# to avoid circular dependencies during the service loading phase.
# from .kernel import Kernel