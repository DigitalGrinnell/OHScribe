# OHScribe!

This is a *Python 3* and *Flask* web application designed to transform oral history transcripts, presumably created using [InqScribe](https://www.inqscribe.com), into XML suitable for ingest into the **[Islandora Oral Histories Solution Pack](https://github.com/Islandora-Labs/islandora_solution_pack_oralhistories)** to populate a TRANSCRIPT datastream and its derivatives.  *Islandora Oral Histories* and the aforementioned solution pack are commonly referred to as **IOH** throughout this document.

**OHScribe!** is intended to be used as part of a broader IOH transcription workflow developed at *Grinnell College*.  The workflow documented in the section titled [InqScribe Workflow](#inqscribe-workflow) may be of significant interest to individuals tasked with transcribing IOH audio recordings.

### Formatted IOH Example

The aforementioned workflow, application, and accompanying CSS (provided below) are intended to deliver oral histories that look something like this:

![IOH Example](https://user-images.githubusercontent.com/8472769/27488663-707973aa-57fd-11e7-98e7-a7994b528ab9.png)

Note that the names of speakers appear in different colors in the video window captions, and speaker names appear in bold in the indexed transcript below the video.  Each speaker and corresponding text appears on a new line, and captions are superimposed over a thumbnail image of the speaker(s).

## InqScribe IOH Transcription Workflow

A detailed description of the workflow intended for use with *OHScribe!* is provided in our [WORKFLOW.md](https://github.com/DigitalGrinnell/OHScribe/blob/master/WORKFLOW.md) document.

## Workflow Output

The workflow documented in the aforementioned *WORKFLOW.md* should produce an XML formatted transcript which resembles the structure of the following example.

~~~
 <transcript>
  <prologue/>
  <scene id="1" in="00:00:00.21" out="00:00:12.07"><speaker> Heather Riggs </speaker>
Heather | Okay, so.. Yeah, just before we start, if you could each go around and say your name, your class year, and where you live now, just for the microphone.</scene>
  <scene id="2" in="00:00:12.08" out="00:00:18.02"><speaker> Margo Gray </speaker>
Margo | Cool. I’m Margo Gray of the class of 2005, and, what else am I saying?</scene>
  <scene id="3" in="00:00:18.03" out="00:00:19.07">Heather | Your home.

<speaker> Maggie Montanaro </speaker>
Maggie | Where you live.</scene>
  <scene id="4" in="00:00:19.08" out="00:00:21.14">Margo | I live in Chicago, Illinois.</scene>
  <scene id="5" in="00:00:21.15" out="00:00:26.07"><speaker> Jenny Noyce </speaker>
Jenny | My name is Jenny Noyce, the class of 2005 and I live in Oakland, California.</scene>
  <scene id="6" in="00:00:26.08" out="00:00:32.11">Maggie | I’m Maggie Montanaro, also class of 2005, and I live in Avignon, France.</scene>
  <scene id="7" in="00:00:32.12" out="00:00:39.17">Heather | Wow. So, what are your strongest memories of Grinnell?</scene>
  <scene id="8" in="00:00:39.18" out="00:00:45.05">Maggie | Harris Parties.</scene>
  <scene id="9" in="00:00:45.06" out="00:00:53.00">Jenny | Mud sliding in the rain.

Maggie | Yeah, mud wrestling. Mud sliding on Mac Field. Lots and lots of work.</scene>
  <scene id="10" in="00:00:53.01" out="00:01:30.27">Margo | I guess I remember people, like, I still am in touch with a lot of people from Grinnell and yeah. So I don’t, I mean I don’t have like
these really specific memories of like meeting people, but just mostly, like this whole sort of like pool of memories of times when I was hanging out with people or working with people or, yeah. Building the sort of, you don’t think of it when you’re there, it’s not like, "Ah, I’m building connections to last me!" You’re just like, "I’m hanging out with my friends." But those sort of things tend to last.

Maggie | Lots of good hanging out.

Margo | Yes.</scene>
  <scene id="11" in="00:01:30.28" out="00:02:01.00">Heather | What kind of Harris parties did you have? Like themed...

Maggie | All the, I assume they still have them, the hall ones like the Haines Underwear Ball, the Mary B. James, Disco... what else? Lots of just themed…

Jenny | They started a fetish party.

Maggie | Really? They still have fetish?

Jenny | I never went to that one. Maybe I was too close-minded.

Maggie | Yeah.</scene>
  <scene id="12" in="00:02:01.01" out="00:02:18.14">Heather | What are your first memories of Grinnell?
~~~

Key parts of this exported transcript example are described in the sections below.

### `<scene>` Tags

`<scene>` tags enclose data indicating who is speaking along with transcribed text from the recording. `<scene>` tags also include attributes indicating the position or scene's *id*, *in* and *out* times provided in hours-minutes-seconds, or *hh:mm:ss.s* notation, and one or more optional `<speaker>` tags.

~~~
<scene id="1" in="00:00:00.21" out="00:00:12.07">
  <speaker> Heather Riggs </speaker>
  Heather | Okay, so.. Yeah, just before we start, if you could each go around and say your name, your class year, and where you live now, just for the microphone.
</scene>
~~~

The example `<scene>` tag shown above carries an *id* of '1', it's the first scene in the transcript, with *in* and *out* times provided in hours-minutes-seconds, or *hh:mm:ss.s* notation.  The *in* and *out* attributes indicate when the transcribed text is heard in the audio stream.  This scene also encloses a `<speaker>` tag which, in this case, identifies the speaker "Heather", as an individual with a full name of "Heather Riggs".   

The text of this scene, a single sentence, opens with a required `speaker ID`, the name of the speaker, *Heather*, followed by a pipe (|) delimiter.  

This demonstrates an important rule... **Each line of transcribed text MUST begin with a *speaker ID*, a given/first name, or single word identifying the speaker, followed by a pipe delimiter.**

~~~
<scene id="11" in="00:01:30.28" out="00:02:01.00">
  Heather | What kind of Harris parties did you have? Like themed...
  Maggie | All the, I assume they still have them, the hall ones like the Haines Underwear Ball, the Mary B. James, Disco... what else? Lots of just themed…
  Jenny | They started a fetish party.
  Maggie | Really? They still have fetish?
  Jenny | I never went to that one. Maybe I was too close-minded.
  Maggie | Yeah.  
</scene>  
~~~

The example `<scene>` tag shown above, with an *id* of '11', includes *in* and *out* time attributes, and seven lines of transcribed text.  Each line begins with a *speaker ID*, in this case the given/first name of the speaker followed by a pipe (|) delimiter.  Note that this scene has NO `<speaker>` tags because the speakers: Heather, Maggie, and Jenny; all have corresponding `<speaker>` tags inside previous scenes.   

### `<speaker>` Tags

`<speaker>` tags are used to identify each speaker in a transcript by providing their full name, and associating the given/first name portion of their full name with subsequent *speaker ID* prefixes.  

**At least one `<speaker>` tag must appear for each *speaker ID* used in the transcript, and a speaker's tag must appear BEFORE any/all corresponding *speaker ID*s.**

A `<speaker>` must occur only within an enclosing `<scene>` tag.  

### Speaker ID

As previously mentioned, a *speaker ID* identifies a speaker by their given/first name or some single-word identifying term, like "Interviewer"or "Interviewee".  Each *speaker ID* consists of a given/first name, or other single-word identifier, followed by a pipe (|) delimiter.

Spaces around pipe delimiters are recommended, but not required.    

## XML for Ingest into IOH

The Islandora Oral Histories (IOH) solution pack expects a TRANSCRIPT datastream of `<cues>` formatted like the following for successful ingest.

~~~
<cues>
  <cue>
    <speaker>Heather Riggs</speaker>
    <start>0.21</start>
    <end>12.07</end>
    <transcript>&lt;span class='oh_speaker_1'&gt;Heather: &lt;span class='oh_speaker_text'&gt; Okay, so.. Yeah, just before we start, if you could each go around and say your name, your class year, and where you live now, just for the microphone.&lt;/span&gt;&lt;/span&gt;</transcript>
  </cue>
  <cue>
    <speaker>Margo Gray</speaker>
    <start>12.08</start>
    <end>18.02</end>
    <transcript>&lt;span class='oh_speaker_2'&gt;Margo: &lt;span class='oh_speaker_text'&gt; Cool. I&#8217;m Margo Gray of the class of 2005, and, what else am I saying?&lt;/span&gt;&lt;/span&gt;</transcript>
  </cue>
  <cue>
    <speaker>Heather Riggs &amp; Maggie Montanaro</speaker>
    <start>18.03</start>
    <end>19.07</end>
    <transcript>&lt;span class='oh_speaker_1'&gt;Heather: &lt;span class='oh_speaker_text'&gt; Your home.&lt;/span&gt;&lt;/span&gt;&lt;span class='oh_speaker_3'&gt;Maggie: &lt;span class='oh_speaker_text'&gt; Where you live.&lt;/span&gt;&lt;/span&gt;</transcript>
  </cue>
  <cue>
    <speaker>Margo Gray</speaker>
    <start>19.08</start>
    <end>21.14</end>
    <transcript>&lt;span class='oh_speaker_2'&gt;Margo: &lt;span class='oh_speaker_text'&gt; I live in Chicago, Illinois.&lt;/span&gt;&lt;/span&gt;</transcript>
  </cue>
  <cue>
    <speaker>Jenny Noyce</speaker>
    <start>21.15</start>
    <end>26.07</end>
    <transcript>&lt;span class='oh_speaker_4'&gt;Jenny: &lt;span class='oh_speaker_text'&gt; My name is Jenny Noyce, the class of 2005 and I live in Oakland, California.&lt;/span&gt;&lt;/span&gt;</transcript>
  </cue>
  <cue>
    <speaker>Maggie Montanaro</speaker>
    <start>26.08</start>
    <end>32.11</end>
    <transcript>&lt;span class='oh_speaker_3'&gt;Maggie: &lt;span class='oh_speaker_text'&gt; I&#8217;m Maggie Montanaro, also class of 2005, and I live in Avignon, France.&lt;/span&gt;&lt;/span&gt;</transcript>
  </cue>
 ~~~

In this format each `<cue>` tag within the enclosing `<cues>` tag represents one `<scene>` from the previously documented workflow output.  Like a `<scene>`, each `<cue>` identifies a speaker, a start and end time, and one or more lines of transcribed text.

**OHScribe!** can be used to transform output from the documented workflow into this format for ingest.  

## Running OHScribe!

**OHScribe!** is accessible at https://ohscribe.grinnell.edu and should run in any web browser.  It permits a user to upload an XML file, output from the aforementioned workflow, and if successful, it provides an output file in IOH-compatible XML format as a download.  Since upload and download of content is provided the site will present the user with a required login screen like this:

  

 Once installed you should run the script using a command like the following (you can easily create an alias and use that if you like):

~~~
python /path/to/script/Transform_InqScribe_to_IOH.py
~~~

Doing so should launch a simple GUI that looks like this:

![screen shot 2017-06-23 at 9 15 33 am](https://user-images.githubusercontent.com/8472769/27486523-80966e2a-57f6-11e7-9399-ab9ec15e6dd8.png)

## Typical Use

You typically use this script like so:

1) Click the __Browse__ button and navigate to a transcript XML file prepared in and exported from InqScribe.  

    > This action opens the selected XML file for processing with the path to the file reflected in the box at the top of the GUI.

2) Click the __Transform InqScribe to IOH XML__ button.  

    > This action invokes the XSLT in __Transform_InqScribe_to_IOH.xsl__ to transform the InqScribe XML \<transcript> and \<scene> tags into \<cues> and \<cue> tags reqiured for IOH ingest. It also transforms 'in' and 'out' attributes to \<start> and \<end> tags, and wraps the text of each \<scene> inside \<transcript> tags within each \<cue>. Changes are saved in a new XML file named to match the input filename prefixed by **IOH-**.  The new file is automatically 'selected' and its path now appears in the box at the top of the GUI.

3) Click the __Convert hh:mm:ss to Seconds__ button.

    > This action converts \<start> and \<end> values from hours:minutes:seconds notation to the decimal seconds notation required for IOH. The changes are saved directly in the selected **IOH-** file. This file should be suitable for ingest into IOH.

4) Optionally click the __Format Speakers__ button.

    > This action detects any/all \<speaker> tags in the XML file and enumerates the speakers for subsequent formatting.  It then re-reads the file looking for the first name (one word only!) of an enumerated speaker followed by a pipe (vertical bar character). Pipes are converted to colons.  The following are all valid samples of speaker identifiers and transcript text taken from our example:

        Heather | Okay, so..
        Margo| Cool.
        Maggie | Where you live.
        Jenny| My name is Jenny

    >The preceeding transcript snippet would be transformed to read as follows:

        Heather: Okay, so..
        Margo: Cool.
        Maggie: Where you live.
        Jenny: My name is Jenny

    > If there are no errors, the format changes are written directly into the selected **IOH-** file.  This file should be suitable for ingest into IOH with formatted speaker names.




## CSS Required for Speaker Formatting

To take advantage of the script's "speaker formatting" capabilities you must add the following CSS, or something very similar, to your theme.  This CSS produces coloring and formatting like that shown in the example above.

~~~
/* Color, display and font additions for Oral Histories */
div.tier.active span {
  font-weight: bold;
}
div.tier.active span,
div.tier.active span span.oh_speaker_text {
  color: black !important;
}
div.tier.active span span.oh_speaker_text {
  font-weight: normal !important;
}
span.oh_speaker_text {
  color: #ffff00 !important;     /* yellow */
}
span.oh_speaker_1 {
  display: block;
  color: #00ffff;     /* aqua */
}
span.oh_speaker_2 {
  display: block;
  color: #80ff00;     /* bright green */
}
span.oh_speaker_3 {
  display: block;
  color: #ff0000;     /* bright red */
}
span.oh_speaker_4 {
  display: block;
  color: #ff00ff;     /* fuchsia */
}
span.oh_speaker_5 {
  display: block;
  color: #ffbf00;     /* orange */
}
~~~

## New "Reformat an Old Transcript" Feature

In June 2017 an additional "Reformat an Old Transcript" feature was added to the script.  This feature may be specific to Grinnell College and to Digital Grinnell (https://digital.grinnell.edu), but it could easily be re-purposed for other, similar features.

The feature, as currently written, is designed to add speaker-formatting to older XML.  Specificaly, it converts XML of the form...

~~~
<cues>
  <cue>
    <speaker>Camarin Madigan</speaker>
    <start>0.16</start>
    <end>45.29</end>
    <transcript>My name is Camarin Madigan. When I went to Grinnell my name was... </transcript>
  </cue>
  ...
</cues>
~~~

...into speaker-formatted XML of the form...

~~~
<cues>
  <cue>
    <speaker>Camarin Madigan</speaker>
    <start>0.16</start>
    <end>45.29</end>
    <transcript>&lt;span class='oh_speaker_1'&gt;Camarin: &lt;span class='oh_speaker_text'&gt;My name is Camarin Madigan. When I went to Grinnell my name was...&lt;/span&gt;&lt;/span&gt;</transcript>
  </cue>
  ~~~
