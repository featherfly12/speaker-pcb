# Speaker PCB

In this github, there is a pcb design that has a total of 1 song!  

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


## Programming the Board
Music from an MP3 file is converted into pure binary 16-bit data at 31.25kHz using scripts in `firmware/media`. The output, `media.bin`, may be flashed onto the chip using an external loader and [STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html). The external loader for this custom PCB was written in the folder `firmware/W25Q128_HAL`, and the actual compiled loader file is  `W25Q128_STM32L433_HAL.stldr`. Once the external memory is programmed with the song, the STM32 itself can be flashed with the `music_player` project using [STM32CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html). 

<mark>**When your design is complete, ask an instructor to verify, and then grab a PCB. Solder on the missing components, and then ask a TA to flash the firmware!**</mark>

Use the `solution-design` KiCAD file as a reference when determining how to orient components on the PCB. We are limited in soldering stations, so don't be discouraged if you aren't able to assemble the PCB during the workshop. You can assemble it during any remaining free time you have at the bootcamp. 

These programs were written with the help of Claude Code / Sonnet 4.6. 
