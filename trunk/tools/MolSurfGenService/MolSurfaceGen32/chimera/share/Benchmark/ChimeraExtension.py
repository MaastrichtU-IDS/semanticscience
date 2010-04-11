import chimera.extension

class Benchmark_EMO(chimera.extension.EMO):
	def name(self):
		return 'Benchmark'
	def description(self):
		return 'Graphics benchmark utility.'
	def categories(self):
		return ['Utilities']
	def icon(self):
		return self.path('indy.png')
	def activate(self):
		self.module().show_benchmark_dialog()
		return None

chimera.extension.manager.registerExtension(Benchmark_EMO(__file__))
