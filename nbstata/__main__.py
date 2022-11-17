from ipykernel.kernelapp import IPKernelApp
from .kernel import PyStataKernel

IPKernelApp.launch_instance(kernel_class=PyStataKernel)
