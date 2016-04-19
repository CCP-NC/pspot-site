
# CASTEP pseudopotential library browser - Help

This website provides a convenient way to access information on CASTEP's
most used pseudopotential libraries, reporting basic information as well as
technical details and validation metrics for each of them. All the
pseudopotentials here reported have been calculated starting with the given
parameters with CASTEP 16.1.1.

The main page is a periodic table reporting all known elements. Clicking on
them a box to the right will visualize some fundamental chemical information
about the element as well as the default pseudopotential for it, and a
button which can show a popup window listing all available pseudopotentials.
From here, by clicking on one of the pseudopotential names, one can proceed 
to another page listing detailed information and plots about it. The meaning
of each of these entries will be detailed in the following sections.


## Basic info

In this section some fundamental information about how the pseudopotential
was calculated is included.

* **Ionic charge**: number of electrons left free to act as "valence" for the
pseudopotential.

* **XC functional**: exchange-correlation functional used for the calculation
of the pseudopotential.

* **Solver**: solver method employed to calculate the potential in the free atom.
CASTEP’s default is the scalar-relativistic method of Koelling and Harmon.


## Cutoffs

This table contains the suggested energy cutoffs for calculations using the
given pseudopotential for different levels of precision, with descriptive
names ranging from _COARSE_ to _EXTREME_.
When planning for a new calculation, a good estimate for the cutoff
to use is, once you've decided on one of these levels, to pick the highest
value from all the pseudopotentials that you're going to use.


## Pseudopotential string

This string is the descriptor that contains all the parameters CASTEP needs to
rebuild the potential, and it can be inserted in the _SPECIES\_POT_ block of a
_.cell_ file. A more detailed description of the meaning of these strings can
be found [here](http://www.tcm.phy.cam.ac.uk/castep/otfg.pdf).


## Valence electronic structure

States occupied by the valence electrons in the all electron solution of the
atom expressed as hydrogenlike orbitals.


## Delta test results

If available, this section gives the results of the Delta test, assessing the
accuracy of pseudopotentials used in ab initio codes against an established
standard. As a general rule, the lower the Delta value, the better the
potential. The data may not be included for all pseudopotential libraries.
All details about how the test is carried out as well as the
results for different codes can be found at the website of the [Center for 
Molecular Modeling](https://molmod.ugent.be/deltacodesdft).


## Plotted data

A drop down menu that allows to choose which plot to visualize. These plots
contain information about the final calculated pseudopotential.

* **Energy convergence**: gives a plot of the calculated energy of the isolated, spherical atom vs. the cutoff used.
Horizontal lines marking the various precision levels are plotted as well.

* **Beta projectors**: projector functions of the non-local pseudopotential
classified by momentum channel.

* **Partial waves**: full (dashed lines) and pseudised (continuous) versions
of the electronic wavefunctions corresponding to the beta projectors.


## Projector details

A table containing details on the projectors, including index, momentum
channel, energy of the corresponding wavefunction, cutoff radius, scheme,
type of the projector (**U**ltrasoft or **N**orm-conserving) and a colour legend
to identify the corresponding lines in the plots. 


## Raw data files

Data for energy convergence, partial waves and beta projectors in ASCII format. Required for Gnuplot plotting as well.


## Plotting files

Gnuplot and XMGrace source files required to reproduce the plots for energy convergence, partial waves and beta projectors.