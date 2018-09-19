
## InqScribe IOH Transcription Workflow

[InqScribe](https://www.inqscribe.com) allows a transcriber to define and use [Snippets](http://docs.inqscribe.com/2.2/snippets.html), short bits of frequently-repeated text, with associated triggers or keyboard [Shortcuts](http://docs.inqscribe.com/2.2/keyboardshortcuts.html) that make it easy to quickly add key elements to a transcript.  The following are samples of *Snippets* and their corresponding *Triggers*/*Shortcuts* used in conjunction with our workflow.

![file-inqscribesnippet1-png](https://gist.githubusercontent.com/McFateM/f4e061eb17ce6d645e51c9d0f2a93814/raw/ff7e69a4a5953149a7dd8f3a86f9565c2e4e7017/InqScribeSnippet1.png)

The above image is an example of a *Snippet* we refer to as a 'Speaker Timecode'.  When triggered, this snippet will insert:

  - A timecode, the `${TIME}` variable portion of the snippet, and
  - A name identifying the speaker providing the transcribed text that will follow.  

In this example the speaker's name is 'Darrell' and that name is followed by a *REQUIRED* space and a pipe character, the vertical bar, in the portion that reads `Darrell |`.

Note also that in this example our *Speaker Timecode* snippet is named `Darrell Fisher` and it is assigned to trigger `KP1` which has a corresponding keyboard shortcut.

![file-inqscribesnippet1-png](https://gist.githubusercontent.com/McFateM/f4e061eb17ce6d645e51c9d0f2a93814/raw/ff7e69a4a5953149a7dd8f3a86f9565c2e4e7017/InqScribeSnippet2.png)

The second image, immediately above, is an example of a *Snippet* we refer to as a 'Raw Timecode'.  When triggered, this snippet will insert:

  - A timecode, the value of the `${TIME}` variable referenced in the snippet, and nothing else.

Note that a *Raw Timecode* has no associated speaker name as it's intended to be used when the speaker name is unknown, or when there isn't time during transcription to pause for identification of the next speaker.

This example *Raw Timecode* snippet is named `{$TIME}` and it is assigned to the `Enter` trigger which generally corresponds to the *Enter* or *Return* key on the keyboard.  

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
