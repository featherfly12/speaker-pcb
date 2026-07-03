# BioE-Bootcamp-PCB-Workshop

In this workshop, you will finish a printed circuit board (PCB) design using [KiCAD](https://www.kicad.org) and export the files for manufacturing. Then, you will receive partially assembled PCBs (of the instructor's design) and will hand-solder on components that were not attached in the automated manufacturing facility at [JLCPCB](https://jlcpcb.com). 

## Board Summary
Your team is interested in building a mini-iPod! The iPod will play 1 full song at the push of a button, and will have adjustable volume via a potentiometer. You absent-mindedly assigned the board design to your teammate (who is not well-suited to electrical engineering) and their design almost worked, but had a few major issues: 

(1) The song start button restarts the song once when pressed, and again when released, even though you set the restart event to trigger only on the falling edge of the switch input voltage. 

(2) After a few seconds of operation, the low-dropout regulator (LDO) for the microcontroller power supply got very hot and started smoking, at which point the PCB was broken. 

(3) It was a little quieter than you hoped. 

It is your job to fix these issues, and KiCAD up a new PCB design! Before we get into these issues, we should talk about the major components of the board. 

| Part | What it is | What it does in this circuit |
|------|-----------|------------------------------|
| STM32L433CCT6 | Microcontroller | Runs your code — reads the song from flash memory and streams it to the speaker amplifier over I2S |
| W25Q128JVEIQ | 16 MB flash memory chip | Stores the raw audio file (like a tiny solid-state drive) so the microcontroller can play it back |
| MAX98357AETE+T | I2S audio amplifier | Takes the digital audio stream from the microcontroller and amplifies it directly via pulse-width modulation (PWM) — rapid switching whose pulse widths track the signal, which the speaker smooths back into sound. This switching design is what makes it a class-D amplifier, and what lets it drive a speaker efficiently from such a small chip. |
| AP2112K-3.3TRG1 | 3.3V Low-dropout Regulator (LDO) | Steps down the input voltage to the stable 3.3V that the microcontroller and other chips need to operate safely. This can eliminate most noise from the power supply, making the 3.3V "clean" power. |
| SMAJ13A | TVS (transient voltage suppression) diode | Prevents voltage spikes on the power input. |
| PESD3V3L4UG,115 | 4-channel ESD protection array | Guards four signal lines at once against static electricity (ESD). Static can silently kill chips when you touch their pins!  |
| PESD3V3L1BA | Single-channel ESD protection diode | Same idea as above, but for one signal line.|
|ECS-80-12-33-JGN-TR | 8MHz Crystal | A crystal that oscillates within 20 ppm of 8MHz when driven by the MCU (with some helper capacitors). This makes the clock of the MCU much more precise, and prevents the frequency of the song from drifting while it is playing. |

Check out the KiCAD project in `music-player-pcb-design` to see the current version of the design!

## Fixing the Switch
The current switch circuit looks like this in the schematic:

<img src="./images/bouncy-switch.png" width="600">

The output of the switch goes to the MCU on pin PB14 - this output node has been labelled "switch" in KiCAD for notational clarity. Unfortunately, this kind of switch can oscillate when it is opened or closed! This has to do with the fact that the metal contacts of the switch literally bounce very briefly when making and breaking contact. These oscillations can be tricky to diagnose on a microcontroller and are called "switch bounce". Digikey suggests the following solution in a brief [application note](https://www.digikey.com/en/articles/how-to-implement-hardware-debounce-for-switches-and-relays):

<img src="./images/debounce.png" alt="Switch debounce circuit. D1 is optional, but makes the switching ON/OFF times independent and identical if R₁ = R₂" width="600">

The principle is that when the switch is opened, the capacitor will charge to the supply voltage through $R_1$ and $D_1$, and when the switch is closed the capacitor will discharge through $R_2$. Since the capacitor is charged through a resistor, the switching is much slower and more controlled, preventing any issues with the MCU. 

Note that $D_1$ is optional, but makes the switching ON/OFF times independent and identical if $R_1 = R_2$. The instructor solution design doesn't have $D_1$, since the charging/discharging times are not critical. 

<mark>**Implement switch debounce for this circuit in KiCAD!**</mark>

### Hint: Capacitor Choice
When a capacitor initially at ground is charged through a resistor to a final supply voltage $V_0$, the voltage on the capacitor follows:
$$ V = V_0 (1 - e^{-t / (RC)}) $$
where $R$ is the resistance of the resistor in ohms and $C$ is the capacitance in farads. Thus, we call $\tau = RC$ the "time-constant" for a resistor-capacitor pair. Suppose you need the device to respond in around 1 millisecond. If you use a standard surface-mount 10k resistor, what capacitor should you use? 

### Hint: Placing New Parts
You can probably use parts that are already in this circuit to complete this task by copying and pasting them from inside the schematic. Alternatively, the following workflow is helpful for adding new parts to the design:

**1. Generate the part symbol.**

This can be completed from scratch, a stock KiCAD part can be duplicated, or **the symbol file can be downloaded from the part vendor**. Mouser has symbols and footprints for almost all their parts, and will generate them for you upon request if they are not available.  

**2. Import the part symbol into the project symbol library.**
- Open the symbol editor
- In the search bar, look for the library called `project_symbols`. This library was generated when the project began by navigating to `Preferences` >> `Manage Symbol Libraries` and navigating to the `Project Specific Libraries` tab and generating a new library. For this workshop, it makes sense to keep all new symbols within `project_symbols`. 
- With `project_symbols` highlighted, select `File` >> `Import` >> `Symbol...`
- Navigate to the symbol file and select it. 

**3. Choose a footprint for the part.**
- A custom footprint can be added to KiCAD by dragging the footprint file, which ends in `.kicad_mod`, into the `footprints` directory. This folder was configured as a project-specific footprint library, visible in `Assign Footprints` >> `Manage Footprint Libraries` >> `Project Specific Libraries`. 
- Alternatively, for standard parts like SMD resistors, KiCAD has an extensive footprint library that can be searched. 
- The footprint for each part must be selected within the symbol properties, before the part is placed in the circuit! It is best only ever to modify the properties of library symbols, rather than the properties of parts that are already placed on the schematic, so that edits propagate to new part instances. 

**4. Fill out remaining fields helpful for BOM generation or internal record-keeping.**
- Examples: Manufacturer Part Number, Manufacturer, JLCPCB Part Number

## Fixing the Power Supply

After examining the schematic, you spot the real problem: stepping a 12V supply down to 3.3V with an LDO wastes most of your power as heat instead of delivering it to the parts of the circuit actually doing useful work. An LDO regulates voltage by acting like a variable resistor in series with the load, dropping whatever voltage is "extra" across itself and dissipating it as heat. If your circuit draws a current $I$ at 3.3V, the microcontroller and speaker only consume $P = 3.3\text{V} \times I$. But the LDO has to drop the remaining $12\text{V} - 3.3\text{V} = 8.7\text{V}$ across itself at that same current $I$, dissipating $P = 8.7\text{V} \times I$ as heat — more than twice what your actual circuit uses. Out of every watt you draw from the 12V supply, less than 30% reaches the microcontroller and speaker; the rest turns into heat inside the LDO. That heat has to go somewhere, and a tiny LDO package has very little surface area to shed it. Unsurprisingly, yours overheated and burned out.

Your solution will be to design a *buck converter*, which uses pulse-width modulation, an inductor, and capacitors to step down 12V to 5V with only very minimal energy loss. We recommend part # AP63205WU-7, from Diodes Inc, but you may design whatever solution you think is most suitable. **The buck converter datasheet is [here](https://www.diodes.com/assets/Datasheets/AP63200-AP63201-AP63203-AP63205.pdf); you will need to reference this datasheet to design the buck converter circuit.** Additionally, we used the following parts in our solution:
- 4.7uH Inductor (MFG CAT # NRS6028T4R7MMGKV, [link](https://www.digikey.com/en/products/detail/taiyo-yuden/NRS6028T4R7MMGKV/4693978?s=N4IgTCBcDaIHICUDKA2ADGAHAFQCwIHYBZIgcQGkA1EAXQF8g))
- 10uF Capacitor (Samsung CAT #: CL31A106KBHNNNE, JLCPCB#: C13585, [link](https://jlcpcb.com/partdetail/14236-CL31A106KBHNNNE/C13585))
- 22uF Capacitor (Samsung CAT #: CL31A226KAHNNNE, JLCPCB#: C12891, [link](https://jlcpcb.com/partdetail/13537-CL31A226KAHNNNE/C12891)) 
- 100nF Capacitor (YAGEO CAT #: CC0603KRX7R9BB104, JLCPCB#: C14663, [link](https://jlcpcb.com/partdetail/YAGEO-CC0603KRX7R9BB104/C14663))

Note that for capacitors, "basic" parts from JLCPCB were used. **This dramatically cuts down automated assembly costs.** You might think it would be fine to hand-assemble your boards, but from personal experience this task can be extremely difficult and time-consuming, and it is nearly always worthwhile to have "basic" parts like resistors and capacitors robotically assembled onto prototypes. 

A benefit of the 5V output from the buck converter is that the speaker driver can now be driven directly from this 5V, rather than from the 3.3V LDO output. The speaker uses the most current in the circuit and benefits from a power supply near the top of its rated supply voltage range. This gives it the most voltage headroom to drive the speaker, resulting in louder audio, and prevents major energy losses in the LDO. Of course, powering the LDO from 5V rather than 12V also dramatically increases circuit efficiency. 

<mark>**Design a buck converter to step down the input 12V to 5V. Then, power the LDO and the speaker driver from the output 5V.**</mark>

To check your design, it's good to run ERC (`Inspect` >> `Electrical Rules Checker`). *KiCAD can raise a bunch of issues that are non-critical (e.g. pins of type power output and power output are connected) that really just reflect that the symbol pins are not correctly configured for the ERC. This is not a huge deal, but perusing the error list will let you know if you accidentally left anything unconnected. It will likely not, however, let you know whether you designed your circuit wrong. That's on you!*

## Designing the PCB
Hopefully now you are happy with your schematic. To transfer your schematic work to the PCB perspective, switch to the PCB view and navigate to `Tools` >> `Update PCB from Schematic`.

<mark>**Place parts and then route copper traces, zones, and vias as necessary so that your PCB reflects the changes that were made in your schematic.**</mark>

Confirm that your design passes some basic checks by running DRC ("Inspect" >> "Design Rules Checker"). Hopefully you shouldn't see any errors worse than "Silkscreen clipped by solder mask" or similar. Be sure to fix any unconnected or incorrectly connected nets. 


## Programming the Board
Music from an MP3 file is converted into pure binary 16-bit data at 31.25kHz using scripts in `firmware/media`. The output, `media.bin`, may be flashed onto the chip using an external loader and [STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html). The external loader for this custom PCB was written in the folder `firmware/W25Q128_HAL`, and the actual compiled loader file is  `W25Q128_STM32L433_HAL.stldr`. Once the external memory is programmed with the song, the STM32 itself can be flashed with the `music_player` project using [STM32CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html). 

<mark>**When your design is complete, ask an instructor to verify, and then grab a PCB. Solder on the missing components, and then ask a TA to flash the firmware!**</mark>

Use the `solution-design` KiCAD file as a reference when determining how to orient components on the PCB. We are limited in soldering stations, so don't be discouraged if you aren't able to assemble the PCB during the workshop. You can assemble it during any remaining free time you have at the bootcamp. 

These programs were written with the help of Claude Code / Sonnet 4.6. 