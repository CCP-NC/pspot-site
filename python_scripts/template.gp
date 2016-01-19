set terminal pngcairo font "cmr10 12" size 800,600
set output "beta.png"
# Set up the four projectors
set xrange [0:<x_max>]
set tics nomirror
set multiplot layout 2,2
set title "<s_title>"
<s_scale_string>
plot "<ppot.elem>_OTF.beta.dat" <s_plot_string>
set title "<p_title>"
<p_scale_string>
plot "<ppot.elem>_OTF.beta.dat" <p_plot_string>
set title "<d_title>"
<d_scale_string>
plot "<ppot.elem>_OTF.beta.dat" <d_plot_string>
set title "<f_title>"
<f_scale_string>
plot "<ppot.elem>_OTF.beta.dat" <f_plot_string>
unset multiplot
set output