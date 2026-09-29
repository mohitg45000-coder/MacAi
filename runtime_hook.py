import sys
import types
import ai_edge_litert.interpreter as litert

tflite_runtime = types.ModuleType("tflite_runtime")
tflite_runtime.interpreter = litert

sys.modules["tflite_runtime"] = tflite_runtime
sys.modules["tflite_runtime.interpreter"] = litert
