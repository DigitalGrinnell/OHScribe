
## InqScribe IOH Transcription Workflow

[InqScribe](https://www.inqscribe.com) allows a transcriber to define and use [Snippets](http://docs.inqscribe.com/2.2/snippets.html), short bits of frequently-repeated text, with associated triggers or keyboard [Shortcuts](http://docs.inqscribe.com/2.2/keyboardshortcuts.html) that make it easy to quickly add key elements to a transcript.  The following are samples of *Snippets* and their corresponding *Triggers*/*Shortcuts* used in conjunction with our workflow.

![file-inqscribesnippet1-png](https://gist.githubusercontent.com/McFateM/f4e061eb17ce6d645e51c9d0f2a93814/raw/ff7e69a4a5953149a7dd8f3a86f9565c2e4e7017/InqScribeSnippet1.png)

The above image is an example of a *Snippet* we refer to as a 'Speaker Timecode'.  When triggered, this snippet will insert:

  - A timecode, the `${TIME}` variable portion of the snippet, and
  - A name identifying the speaker providing the transcribed text that will follow.  

In this example the speaker's name is 'Darrell' and that name is followed by a *REQUIRED* space and a pipe character, the vertical bar, in the portion that reads `Darrell | `. There is a space after the pipe character so as to allow the thranscriber to simply press the triger and then immediately start to type the dialogue into InqScribe. OHScribe does not currently correctly parse a pipe character from other text unless it is surrounded by spaces on either side.

Note also that in this example our *Speaker Timecode* snippet is named `Darrell Fisher` and it is assigned to trigger `KP1` which has a corresponding keyboard shortcut. 

Any additional speakers can be represented in the same way by selecting 'Add' and then filling in the correct information similarly to the example above. 

![file-inqscribesnippet1-png](https://gist.githubusercontent.com/McFateM/f4e061eb17ce6d645e51c9d0f2a93814/raw/ff7e69a4a5953149a7dd8f3a86f9565c2e4e7017/InqScribeSnippet2.png)

The second image, immediately above, is an example of a *Snippet* we refer to as a 'Raw Timecode'.  When triggered, this snippet will insert:

  - A timecode, the value of the `${TIME}` variable referenced in the snippet, and nothing else.

Note that a *Raw Timecode* has no associated speaker name as it's intended to be used when the speaker name is unknown, or when there isn't time during transcription to pause for identification of the next speaker.

This example *Raw Timecode* snippet is named `{$TIME}` and it is assigned to the `Enter` trigger which generally corresponds to the *Enter* or *Return* key on the keyboard.  

OHScribe creates a new cue every time it encounters a timecode, so every timecode should be followed immediately by a newline, speaker name and pipe character. For areas of the recording that are dense with speaker changes, no timecode is needed to transition to the next speaker, i.e. the transcriber can represent a change in speaker by entering a newline and the speaker name and pipe character to start the next speaker's dialogue. This will result in a cue that has mutliple speakers.

## Cruft

The first shortcut or "Snippet" defines:
1) A timecode,
2) \<speaker> tag, and
3) The speaker's first name with trailing pipe.

Snippets like this are intended to be used when a speaker is first encountered in a transcript.

The second snippet defines:
1) A timecode, and
2) The speaker's first name with trailing pipe.

Snippets like this are intended to be used only after the corresponding speaker has been encountered since only one \<speaker> tag is required for each speaker in a given transcript file.


## Export to XML

Once the transcription and timecodes are in place, save the InqScribe file and export it to an XML file by selecting 'File -> Export -> XML'.
