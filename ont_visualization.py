import ontospy
from ontospy.gendocs.viz.viz_html_single import *

g = ontospy.Ontospy("http://webprotege.stanford.edu/RT6rB6apdomRGTqlYC3zoM#Süleyman_Demirel")

v = HTMLVisualizer(g) # => instantiate the visualization object
v.build() # => render visualization. You can pass an 'output_path' parameter too
v.preview() # => open in browser