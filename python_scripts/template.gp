set terminal pngcairo enhanced dashed font "cmr10,12" size 1024,768
set output "<pspot.elem>.beta.png"
# Set up the line styles
set style line 1 lt 1 lc rgb '#ee0000'
set style line 2 lt 1 lc rgb '#0000ee'
set style line 3 lt 1 lc rgb '#00cc66'
set style line 4 lt 1 lc rgb '#ddbb00'
set style line 5 lt 1 lc rgb '#00bbdd'
set style line 6 lt 1 lc rgb '#dd00bb'
set style line 7 lt 1 lc rgb '#ddbb00'
set style line 8 lt 1 lc rgb '#66ddee'
set style line 9 lt 1 lc rgb '#777777'
# Dashed styles
set style line 100 lt 2 lc rgb '#000000'
set style line 101 lt 2 lc rgb '#ee0000'
set style line 102 lt 2 lc rgb '#0000ee'
set style line 103 lt 2 lc rgb '#00cc66'
set style line 104 lt 2 lc rgb '#ddbb00'
set style line 105 lt 2 lc rgb '#00bbdd'
set style line 106 lt 2 lc rgb '#dd00bb'
set style line 107 lt 2 lc rgb '#ddbb00'
set style line 108 lt 2 lc rgb '#66ddee'
set style line 109 lt 2 lc rgb '#777777'
# Set up the four projectors
set xrange [0:<x_max>]
set format y ""
set xtics nomirror
set xlabel "r (a.u.)"
unset ytics
set multiplot layout 2,2
set title "<s_beta_title>"
<s_beta_scale>
plot 0 lc 0 lt 1 notitle, "<pspot.elem>_OTF.beta.dat" <s_beta_plot>
unset arrow
set title "<p_beta_title>"
<p_beta_scale>
plot 0 lc 0 lt 1 notitle, "<pspot.elem>_OTF.beta.dat" <p_beta_plot>
unset arrow
set title "<d_beta_title>"
<d_beta_scale>
plot 0 lc 0 lt 1 notitle, "<pspot.elem>_OTF.beta.dat" <d_beta_plot>
unset arrow
set title "<f_beta_title>"
<f_beta_scale>
plot 0 lc 0 lt 1 notitle, "<pspot.elem>_OTF.beta.dat" <f_beta_plot>
unset arrow
unset multiplot
set autoscale y
# Now do the projector wave thing
set output "<pspot.elem>.pwave.png"
set multiplot layout 2,2
set title "<s_pwave_title>"
<s_pwave_scale>
plot 0 lc 0 lt 1 notitle, "<pspot.elem>_OTF.pwave.dat" <s_pwave_plot>
unset arrow
set title "<p_pwave_title>"
<p_pwave_scale>
plot 0 lc 0 lt 1 notitle, "<pspot.elem>_OTF.pwave.dat" <p_pwave_plot>
unset arrow
set title "<d_pwave_title>"
<d_pwave_scale>
plot 0 lc 0 lt 1 notitle, "<pspot.elem>_OTF.pwave.dat" <d_pwave_plot>
unset arrow
set title "<f_pwave_title>"
<f_pwave_scale>
plot 0 lc 0 lt 1 notitle, "<pspot.elem>_OTF.pwave.dat" <f_pwave_plot>
unset arrow
unset multiplot
set output "<pspot.elem>.econv.png"
set multiplot layout 1,2
unset title
set autoscale
set xlabel "Cutoff energy (eV)"
set ylabel "Energy error (eV/atom)"
set ytics 1
stats "<pspot.elem>_OTF.econv.dat" u 2:3 nooutput
set yrange [(STATS_min_x-(STATS_max_x-STATS_min_x)*0.1):(STATS_max_x+(STATS_max_x-STATS_min_x)*0.1)]
plot "<pspot.elem>_OTF.econv.dat" u 1:2 w l lc 0 lt 1 notitle, 2 w l ls 101 ti "Coarse", 0.3 w l ls 102 ti "Medium", 0.1 w l ls 103 ti "Fine", 0.01 w l ls 104 ti "Extreme"
set key bottom left
set ylabel "Log10 Energy error (eV/atom)"
set yrange [(STATS_min_y-(STATS_max_y-STATS_min_y)*0.1):(STATS_max_y+(STATS_max_y-STATS_min_y)*0.1)]
plot "<pspot.elem>_OTF.econv.dat" u 1:3 w l lc 0 lt 1 notitle, log10(2) w l ls 101 ti "Coarse", log10(0.3) w l ls 102 ti "Medium", log10(0.1) w l ls 103 ti "Fine", log10(0.01) w l ls 104 ti "Extreme"
unset multiplot
set output
