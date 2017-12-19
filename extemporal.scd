(
s.waitForBoot {

	e = ();

	e.words = ['extemporale', 'zone'];

	e.scentences = [
		'reprsentation der ewigkeit in jedem augenblick'
	];

	e.dataDir = Document.current.dir +/+ 'data';

	e.data = {
		var file = File.open(e.dataDir +/+ 'extemporal.sc', "r");
		var data = file.readAllString().interpret();
		file.close;
		data;
	}.value();

	SynthDef(\sampler, {
		|bufnum, vol = 0, pos = 0, fade = 0.02|
		var sig = PlayBuf.ar(1, bufnum, BufRateScale.kr(bufnum), doneAction: 2);
		var env = EnvGen.ar(Env.linen(fade, BufDur.ir(bufnum) - (2*fade), fade));
		Out.ar(0, Pan2.ar(vol.dbamp * env * sig, pos));
	}).add;

	SynthDef(\censor, {
		|vol = 0, dur = 0.1, pos = 0|
		var env = EnvGen.ar(Env.linen(0, dur, 0), doneAction: 2);
		Out.ar(0, Pan2.ar(SinOsc.ar(400, 0,  env * vol.dbamp), pos));
	}).add;

	e.speak = {{
		|scentence|
		postln("say:" + scentence);
		Task {
			var words = scentence.asString.split($ );
			var buffers = Array.fill(words.size(), { |i|
				var segs= e.data.select({|j| j.word == words[i].asSymbol});
				if (segs.size() > 0) {
					var seg = segs.scramble.first;
					var start = seg.start * 48000;
					var numSamples = seg.length * 48000;
					Buffer.read(s, e.dataDir +/+ seg.file, start, numSamples);
				}
			});
			s.sync;
			buffers.do { |buffer|
				if (buffer.notNil, {
					Synth(\sampler, [\bufnum, buffer.bufnum, \pos, rrand(-1.0, 1.0)]);
					wait(buffer.numFrames / buffer.sampleRate);
					buffer.free();
				},  {
					Synth(\censor, [\dur, 0.3, \pos, rrand(-1.0, 1.0)]);
					0.3.wait;
				})
			};
			Tdef(\main).resume;
		}.play;
	}};

	e.blabla = {{
		|numWords|
		postln(numWords.asString + "random words");
		Task {
			var buffers = Array.fill(numWords, { |i|
				var seg= e.data.scramble.first;
				var start = seg.start * 16000;
				var numSamples = seg.length * 16000;
				Buffer.read(s, e.dataDir +/+ seg.file, start, numSamples);
			});
			s.sync;
			buffers.do { |buffer|
				if (buffer.notNil, {
					Synth(\sampler, [\bufnum, buffer.bufnum, \pos, rrand(-1.0, 1.0)]);
					wait(buffer.numFrames / buffer.sampleRate);
					buffer.free();
				},  {
					Synth(\censor, [\dur, 0.3, \pos, rrand(-1.0, 1.0)]);
					0.3.wait;
				})
			};
			Tdef(\main).resume;
		}.play;
	}};

	e.all = {{
		|word|
		postln("all of:" + word);
		Task {
			var segs= e.data.select({|j| j.word == word.asSymbol}).scramble;
			var buffers = Array.fill(segs.size, { |i|
				var seg= segs[i];
				var start = seg.start * 16000;
				var numSamples = seg.length * 16000;
				Buffer.read(s, e.dataDir +/+ seg.file, start, numSamples);
			});
			s.sync;
			buffers.do { |buffer|
				if (buffer.notNil, {
					Synth(\sampler, [\bufnum, buffer.bufnum, \pos, rrand(-1.0, 1.0)]);
					wait(buffer.numFrames / buffer.sampleRate);
					buffer.free();
				},  {
					Synth(\censor, [\dur, 0.3, \pos, rrand(-1.0, 1.0)]);
					0.3.wait;
				})
			};
			Tdef(\main).resume;
		}.play;
	}};

	Tdef(\main, { loop {
		[
			{e.speak.value(e.scentences.choose)},
			{e.blabla.value(10.rand)},
			{e.all.value(e.words.choose)}
		].choose.value;
		Tdef(\main).pause;
		1.wait;
	}}).play;
}
)

