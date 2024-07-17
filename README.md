# BLosCode (v1.0)

Recent surveys and telescopes have extensively observed the plane-of-sky component of magnetic fields in molecular clouds, but observations of their line-of-sight magnetic fields remain limited. To address this gap, we developed MC-BLOS (v1.0), an automated software implementation of the Faraday rotation-based technique introduced by Tahani et al. (2018).

Key Features:
- Input: Faraday rotation of point sources (extra-galactic sources or pulsars), extinction or column density maps, chemical evolution code results, and a configurable text/CSV file for cloud-specific parameters.
- Predefined initial parameters (density, temperature, surrounding boundary) for each cloud, with user modification options.
- Automated execution of the technique, outputting line-of-sight magnetic field maps and tables with uncertainties.
- Significant reduction in analysis time compared to manual methods.

The software has been validated against previously-published cloud data, producing results consistent within uncertainty ranges. MC-BLOS is poised to facilitate the analysis of forthcoming Faraday rotation observations associated with molecular clouds.
