set terminal pngcairo enhanced dashed font "cmr10,12" size 1024,768
set output "beta.png"
# Set up the four projectors
set xrange [0:<x_max>]
set format y ""
set xtics nomirror
set xlabel "r (Ang)"
unset ytics
set multiplot layout 2,2
set title "<s_beta_title>"
<s_beta_scale>
plot 0 lc 0 lt 1 notitle, "<ppot.elem>_OTF.beta.dat" <s_beta_plot>
unset arrow
set title "<p_beta_title>"
<p_beta_scale>
plot 0 lc 0 lt 1 notitle, "<ppot.elem>_OTF.beta.dat" <p_beta_plot>
unset arrow
set title "<d_beta_title>"
<d_beta_scale>
plot 0 lc 0 lt 1 notitle, "<ppot.elem>_OTF.beta.dat" <d_beta_plot>
unset arrow
set title "<f_beta_title>"
<f_beta_scale>
plot 0 lc 0 lt 1 notitle, "<ppot.elem>_OTF.beta.dat" <f_beta_plot>
unset arrow
unset multiplot
set autoscale y
# Now do the projector wave thing
set output "pwave.png"
set multiplot layout 2,2
set title "<s_pwave_title>"
<s_pwave_scale>
plot 0 lc 0 lt 1 notitle, "<ppot.elem>_OTF.pwave.dat" <s_pwave_plot>
unset arrow
set title "<p_pwave_title>"
<p_pwave_scale>
plot 0 lc 0 lt 1 notitle, "<ppot.elem>_OTF.pwave.dat" <p_pwave_plot>
unset arrow
set title "<d_pwave_title>"
<d_pwave_scale>
plot 0 lc 0 lt 1 notitle, "<ppot.elem>_OTF.pwave.dat" <d_pwave_plot>
unset arrow
set title "<f_pwave_title>"
<f_pwave_scale>
plot 0 lc 0 lt 1 notitle, "<ppot.elem>_OTF.pwave.dat" <f_pwave_plot>
unset arrow
unset multiplot
set output "econv.png"
set multiplot layout 1,2
unset title
set autoscale
set xlabel "Cutoff energy (eV)"
set ylabel "Energy error (eV/atom)"
stats "<ppot.elem>_OTF.econv.dat" u 2:3 nooutput
set yrange [(STATS_min_x-(STATS_max_x-STATS_min_x)*0.1):(STATS_max_x+(STATS_max_x-STATS_min_x)*0.1)]
plot "<ppot.elem>_OTF.econv.dat" u 1:2 w l lc 0 lt 1 notitle, 2 w l lc 1 lt 2 ti "Coarse", 0.3 w l lc 2 lt 2 ti "Medium", 0.1 w l lc 3 lt 2 ti "Fine", 0.01 w l lc 4 lt 2 ti "Extreme"
set ylabel "Log10 Energy error (eV/atom)"
set yrange [(STATS_min_y-(STATS_max_y-STATS_min_y)*0.1):(STATS_max_y+(STATS_max_y-STATS_min_y)*0.1)]
plot "<ppot.elem>_OTF.econv.dat" u 1:3 w l lc 0 lt 1 notitle, log10(2) w l lc 1 lt 2 ti "Coarse", log10(0.3) w l lc 2 lt 2 ti "Medium", log10(0.1) w l lc 3 lt 2 ti "Fine", log10(0.01) w l lc 4 lt 2 ti "Extreme"
unset multiplot
set output