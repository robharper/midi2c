# MIDI to C-arrays

> Converts a midi file to C-formatted arrays of note frequencies and millisecond timings for use in arduino projects

See https://github.com/robharper/3-stepper-mario for example usage

### Requirements

```
pip install midi
```

### Example
*Usage:* `python midi2c.py mario.mid`

*Input:* mario brothers midi file

*Output:*
```
// Length of part
const int part0Len = 1128;
// Frequencies
const int part0F[] PROGMEM = {
Fs4, Fs4, silence, Fs4, silence, Fs4, Fs4, silence, G4, silence, G4, silence, E4, silence, C4, silence, G3, silence, C4, silence, D4, silence, Cs4, C4, silence, C4, silence, G4, silence, B4, silence, C5, silence, A4, B4, silence, A4, silence, E4, F4, D4, silence, E4, silence, C4, silence, G3, silence, C4, silence, D4, silence, Cs4, C4, silence, C4, silence, G4, silence, B4, silence, C5, silence, A4, ... };
// Times in milliseconds
const int part0T[] PROGMEM = {
152, 149, 149, 148, 154, 149, 148, 149, 154, 446, 154, 468, 159, 293, 148, 303, 148, 303, 149, 152, 150, 152, 149, 148, 154, 105, 98, 100, 100, 97, 100, 154, 149, 148, 148, 155, 149, 148, 148, 154, 149, 313, ... };
...
```

### Other
`freqs.py` generates `#define`s for the note definitions above

### Attribution
Modified version of https://github.com/starfys/midi2csv
