#!/usr/bin/python2
import midi
import sys

MAX_VOICES = 3
MIN_SILENCE_MS = 5

# MIDI note number to text representation
note_lookup = ['silence'] * 108
# Limited octave range
#2
note_lookup[36] = 'C2'
note_lookup[37] = 'Cs2'
note_lookup[38] = 'D2'
note_lookup[39] = 'Ds2'
note_lookup[40] = 'E2'
note_lookup[41] = 'F2'
note_lookup[42] = 'Fs2'
note_lookup[43] = 'G2'
note_lookup[44] = 'Gs2'
note_lookup[45] = 'A2'
note_lookup[46] = 'As2'
note_lookup[47] = 'B2'
#3
note_lookup[48] = 'C3'
note_lookup[49] = 'Cs3'
note_lookup[50] = 'D3'
note_lookup[51] = 'Ds3'
note_lookup[52] = 'E3'
note_lookup[53] = 'F3'
note_lookup[54] = 'Fs3'
note_lookup[55] = 'G3'
note_lookup[56] = 'Gs3'
note_lookup[57] = 'A3'
note_lookup[58] = 'As3'
note_lookup[59] = 'B3'
#4
note_lookup[60] = 'C4'
note_lookup[61] = 'Cs4'
note_lookup[62] = 'D4'
note_lookup[63] = 'Ds4'
note_lookup[64] = 'E4'
note_lookup[65] = 'F4'
note_lookup[66] = 'Fs4'
note_lookup[67] = 'G4'
note_lookup[68] = 'Gs4'
note_lookup[69] = 'A4'
note_lookup[70] = 'As4'
note_lookup[71] = 'B4'
#5
note_lookup[72] = 'C5'
note_lookup[73] = 'Cs5'
note_lookup[74] = 'D5'
note_lookup[75] = 'Ds5'
note_lookup[76] = 'E5'
note_lookup[77] = 'F5'
note_lookup[78] = 'Fs5'
note_lookup[79] = 'G5'
note_lookup[80] = 'Gs5'
note_lookup[81] = 'A5'
note_lookup[82] = 'As5'
note_lookup[83] = 'B5'
#6
note_lookup[84] = 'C6'
note_lookup[85] = 'Cs6'
note_lookup[86] = 'D6'
note_lookup[87] = 'Ds6'
note_lookup[88] = 'E6'
note_lookup[89] = 'F6'
note_lookup[90] = 'Fs6'
note_lookup[91] = 'G6'
note_lookup[92] = 'Gs6'
note_lookup[93] = 'A6'
note_lookup[94] = 'As6'
note_lookup[95] = 'B6'
#7
note_lookup[96] = 'C7'
note_lookup[97] = 'Cs7'
note_lookup[98] = 'D7'
note_lookup[99] = 'Ds7'
note_lookup[100] = 'E7'
note_lookup[101] = 'F7'
note_lookup[102] = 'Fs7'
note_lookup[103] = 'G7'
note_lookup[104] = 'Gs7'
note_lookup[105] = 'A7'
note_lookup[106] = 'As7'
note_lookup[107] = 'B7'

def compare(event1, event2):
    if event1[0] < event2[0]:
        return -1
    elif event1[0] > event2[0]:
        return 1
    else:
        if event1[2] == 0:
            return 1
        if event2[2] == 0:
            return -1
        return 0


pattern = midi.read_midifile(sys.argv[1])
tempo = 500000.0
resolution = pattern.resolution * 1.0
#output_file = open(sys.argv[2], 'w+')
events = []
for track in pattern:
    track.make_ticks_abs()
    for event in track:
        events.append(event)
#Used to keep track of note positions
turned_on = {}
#Used to keep track of played notes
notes = []
for event in events:
    if type(event) == midi.NoteOnEvent:
        turned_on[event.data[0]] = event.tick
        if event.data[1] == 0:
            notes.append((turned_on[event.data[0]], event.data[0], event.tick - turned_on[event.data[0]]))
            turned_on.pop(event.data[0], None)
    elif type(event) == midi.NoteOffEvent:
        try:
            notes.append((turned_on[event.data[0]], event.data[0], event.tick - turned_on[event.data[0]]))
            turned_on.pop(event.data[0], None)
        except:
            pass
    elif type(event) == midi.SetTempoEvent:
        notes.append((event.tick, (((event.data[0]*65536)+event.data[1]*256+event.data[2])), 0))
notes = sorted(notes,cmp=compare)

final_notes = []
last_time = 0.0
last_ticks = 0
for note in notes:
    if note[2] == 0:
        tempo = note[1]
        continue
    next_time = last_time + ((tempo * (note[0] - last_ticks)) / (resolution * 1000000))
    final_notes.append((next_time, note[1], (tempo * note[2]) / (resolution * 1000000)))
    last_ticks = note[0]
    last_time = next_time

# Create per-voice arrays
voice_index = 0
last_time = -1
voices = [[] for _ in range(MAX_VOICES)]
voice_offs = [0] * MAX_VOICES
for note in final_notes:
    time = round(note[0]*1000)
    duration = round(note[2]*1000)

    # Next time stamp, back to voice 0
    if time != last_time:
        voice_index = 0
        last_time = time

    # Use the next voice if this one is occupied
    if voice_index < MAX_VOICES-1 and time+5 < voice_offs[voice_index]:
        voice_index += 1
    if voice_index < MAX_VOICES-1 and time+5 < voice_offs[voice_index]:
        voice_index += 1

    # More voices that we support - drop it
    if voice_index >= MAX_VOICES:
        print 'dropped note'
        continue

    # Add silence if this voice ended prior to timestamp (5ms of acceptable slop)
    if time > voice_offs[voice_index] + MIN_SILENCE_MS:
        # Need to insert some silence before this note
        voices[voice_index].append(['silence', time - voice_offs[voice_index]])

    # Add note
    voices[voice_index].append([note_lookup[note[1]], duration])
    voice_offs[voice_index] = time + duration
    voice_index += 1

# Write all the data in C-code formatting for copy-paste to arduino
for idx, voice in enumerate(voices):
    print "const int part%dLen = %d;" % (idx, len(voice))
    print "const int part%dF[] PROGMEM = {" % idx
    for note in voice:
        sys.stdout.write("%s, " % note[0])

    print "};"
    print "const int part%dT[] PROGMEM = {" % idx
    for note in voice:
        sys.stdout.write("%d, " % note[1])

    print "};"
    print "// ---------------------"
