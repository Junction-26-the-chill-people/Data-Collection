This is the README file for the dataset **N**etherlands **F**orensic **I**nstitute: **F**orensic **A**ctivity **Re**cognition **D**ataset ([NFI_FARED](https://huggingface.co/datasets/NetherlandsForensicInstitute/NFI_FARED_Digital_Traces)). Two forms of data were collected: Digital Traces from iPhones worn on the subjects' bodies, and raw sensor signals from body-worn Inertial Measurement Units (IMUs). This dataset and README refers to the Digital Trace data. The IMU data is available [here](https://huggingface.co/datasets/NetherlandsForensicInstitute/NFI_FARED_IMU).

Published as a part of the paper "[Forensic Activity Classification Using Digital Traces from iPhones: A Machine Learning-based Approach](https://arxiv.org/abs/2512.03786)". 

NFI_FARED contains Digital Trace data from 14 participants (8 male, 6 female), aged 26.6 ± 8.8 years old. Each subject carried four iPhones simultaneously during the data collection. The models and iOS versions are: 6+ (11.4.1), 7 (14.7.1), 11 (13.1.1), and XR (15.4.1). For further details on the data collection procedure, please refer to the [paper](https://arxiv.org/abs/2512.03786). 

Data is extracted from the databases `cache_encryptedC.db` and `healthdb_secure.sqlite` from the iPhones after the data collection experiments and processed into `.pkl` files using proprietary scripts at the NFI.

The datafiles `df_dict_motionstate.pkl`, `df_dict_natalie.pkl`, `df_dict_stepcounthistory.pkl` contain data extracted from the tables `MotionStateHistory`, `NatalieHistory` and `StepCountHistory`, respectively, from the file `cache_encryptedC.db`.

The datafiles `df_dict_healthdb_floors.pkl`, `df_dict_healthdb_distance.pkl`, `df_dict_healthdb_steps.pkl` contain data pertaining to steps, distances and floors extracted from the tables `sample` and `quantity_samples` from the file `healthdb_secure.sqlite`

In all datafiles, columns containing experimental metadata have column names with prefix `META_`. These are:

- `META_carrying_location`: Carry location of the iPhone. Value is one of 'hand', 'frontpocket', ‘backpocket, 'breastpocket', or 'rucksack'.

- `META_telephone_type`: Type of iPhone. Value is one of 'Iphone6+\_IOS\_11.4.1', 'IphoneXR\_IOS\_15.4.1', 'Iphone11\_IOS\_13.1.1', or 'Iphone7\_IOS\_14.7.1'

- `META_test_subject`: Subject ID number

- `META_experiment`: number of experimental session

- `META_label_activity`: assigned ground-truth activity for the corresponding registration.

Activity labels are as follows: `standing, sitting, walking, running, train, car, tram, bus, cycling, stair_up, stair_down, escalator_down, escalator_up, elevator_down, elevator_up, dragging, throwing, punching, kicking` .
Rows labeled `no activity` are from untracked moments in the recording sessions e.g. going from the office where the iPhones were provided to the starting location. There are no assurances on the activities performed (or not performed) in these periods.

Other columns in the datafiles contain data registered by the phones. Variable names are the same as in the original databases. Timestamps `startTime`, `start_date` and `end_date` have been converted from Apple epoch to local time and `(local time)` has been appended to the column name, e.g. `startTime (local time)`. Original epoch time has `(epoch)` appended to columns where it is still present, e.g. `startTime (epoch)`. 

Digital Traces are in general not logged at regular intervals, so traces from different databases are likely not to be aligned in time. For this reason we recommend aggregating traces from the different databases to larger, e.g. one minute, intervals to achieve consistency. Python scripts for processing the `.pkl` files into `.csv` files aggregated at specified intervals can be found on the project [GitHub](https://github.com/Con-or-McCarthy/Data2Activity_1)  .
### Citation
If you wish to use this dataset in your research please cite:
```
@misc{mccarthy2025forensicactivityclassificationusing,
      title={Forensic Activity Classification Using Digital Traces from iPhones: A Machine Learning-based Approach}, 
      author={Conor McCarthy and Jan Peter van Zandwijk and Marcel Worring and Zeno Geradts},
      year={2025},
      eprint={2512.03786},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2512.03786}, 
}
```
### Contact
For questions regarding the data processing, the paper, and/or project GitHub please contact Conor McCarthy: c.t.mccarthy@uva.nl

For questions regarding the data collection please contact Jan Peter van Zandwijk: j.p.van.zandwijk@nfi.nl 