	function isMsgCorrect(msg) {
		var s = msg;
		s = s.toLowerCase();
		s = s.replace(/[\s*\n*]/g,'');
		var isCorrect = true;
		if (s.length == 0) {
			s = "Parsing empty message is impossible!";
			isCorrect = false;
		}
		else if (s.search(/[^a-f\d]/) != -1) {
			s = "DC message is incorrect!";
			isCorrect = false;
		}
		return [isCorrect, s];
	}
	
	function getDncsIp(msg) {
		var dncsIP = '';
		dncsIP += parseInt(msg.substr(0,2),16) + '.' + parseInt(msg.substr(2,2),16) + '.' +
		parseInt(msg.substr(4,2),16) + '.' + parseInt(msg.substr(6,2),16);
		return dncsIP;
	}

	function getStartTimestamp(msg) {
		var startTimestamp = 0;
		startTimestamp = new Date(parseInt(msg.substr(0,8),16)*1000);
		return startTimestamp.toUTCString();
	}
	
// Decoder7bit returns parsed int parameter and length of this parameters (in symbols) in parsed string	
	function Decoder7bit(msg) {
		var tmp = stringParameter = ''; 
		var parameter = isNext = 0;
		for(var i = 0; true; i++) {
			tmp = msg.substring(2*i,2*i+2);
			stringParameter += tmp;
			parameter += parseInt(tmp,16) <<(7*i);
			isNext = parseInt(tmp,16) >> 7;
			if (isNext == 1) {
				parameter -= 1<<(7*(i+1));
			}
			else {
				break;
			}
		}
		return [parameter, stringParameter.length];
	}
	
	function getASCIISymbol(symbolByte) {
		return String.fromCharCode(parseInt('0x'+symbolByte));
	}

// textDecoder returns string parameter text and length of this string in parsed message msg	
	function textDecoder(msg) {
		var text = '';
		returned7bitArray = Decoder7bit(msg);
		var textLength = returned7bitArray[0];
		var tmp = msg.substring(returned7bitArray[1],msg.length);
		for(var i = 0; i < textLength; i++) {
			text += getASCIISymbol(tmp.substring(2*i, 2*i+2));
		}	
		return [text, textLength*2+returned7bitArray[1]];
	}

//	commonPart returns parsed parameters from common part as string and left unparsed string
	function commonPart(msg) {
		var tmp = msg;
		
		var s = 'dncs_ip: ' + getDncsIp(tmp) + '\n';
		tmp = tmp.substring(8,tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'hubid: ' + returned7bitArray[0] + '\n';
		tmp = tmp.substring(returned7bitArray[1],tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'version: ' + returned7bitArray[0] + '\n';
		tmp = tmp.substring(returned7bitArray[1],tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		recordsNumber = returned7bitArray[0];
		s += 'records in array of launched services: ' + recordsNumber + '\n';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		if (recordsNumber > 0) {
			s += 'lanched services: ';
			for (var i = 0; i < recordsNumber; i++) {
				returnedTextArray = textDecoder(tmp);
				s += returnedTextArray[0] + ', ';
				tmp = tmp.substring(returnedTextArray[1], tmp.length);
			}
			s = s.substring(0, s.length-2) + '\n';
		}
		
		returned7bitArray = Decoder7bit(tmp);
		recordsNumber = returned7bitArray[0];
		s += 'records in array of used callsigns: ' + recordsNumber + '\n';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		if (recordsNumber > 0) {
			s += 'used callsigns: ';
			for (var i = 0; i < recordsNumber; i++) {
				returnedTextArray = textDecoder(tmp);
				s += returnedTextArray[0] + ', ';
				tmp = tmp.substring(returnedTextArray[1], tmp.length);
			}
			s = s.substring(0, s.length-2) + '\n';
		}
		return [s, tmp];
	}

//	each event[i] returns parsed parameters for indicated event_id as string and left unparsed string	
	function event0(msg) {
		var tmp = msg;
		var s = ' Mosaic session\n\t';
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'callsign: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'duration: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'exit_type: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'exit_value: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'banner_code: ' + returned7bitArray[0] + '\n';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		return [s, tmp];
	}
	
	function event1(msg) {
		var tmp = msg;
		var s = ' Ace/Upsell menu item enter\n\t';
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'menu_id: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'duration: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'exit_type: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'exit_value: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'banner_code: ' + returned7bitArray[0] + '\n';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		return [s, tmp];
	}	

	function event2(msg) {
		var tmp = msg;
		var s = ' Banner impression\n\t';
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'source: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'banner_id: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'duration: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'activated: ' + returned7bitArray[0] + '\n';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		return [s, tmp];
	}		

	function event3(msg) {
		var tmp = msg;
		var s = ' Upsell order now\n\t';
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'menu_id: ' + returned7bitArray[0] + '\n';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
				
		return [s, tmp];
	}

	function event4(msg) {
		var tmp = msg;
		var s = ' EBIF app session\n\t';
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'app: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'duration: ' + returned7bitArray[0] + '\n';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		return [s, tmp];
	}		

	function event5(msg) {
		var tmp = msg;
		var s = ' Searches count\n\t';
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'count: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'filters: ' + returned7bitArray[0] + '\n';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		return [s, tmp];
	}	

	function event6(msg) {
		var tmp = msg;
		var s = ' Search option activation\n\t';
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'search_element_code: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'duration: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'exit_type: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'exit_value: ' + returned7bitArray[0] + '\n';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		return [s, tmp];
	}	

	function event7(msg) {
		var tmp = msg;
		var s = ' Upsell from Search\n\t';
		
		returnedTextArray = textDecoder(tmp);
		s += 'purchaseValue: ' + returnedTextArray[0] + '\n';
		tmp = tmp.substring(returnedTextArray[1], tmp.length);
				
		return [s, tmp];
	}
	
	function event8(msg) {
		var tmp = msg;
		var s = ' Channel Tunes\n\t';
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'channel_number: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);

		returned7bitArray = textDecoder(tmp);
		s += 'callsign: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		array_size = returned7bitArray[0];
		s += 'array_size: ' + array_size + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		for (var i = 0; i < array_size; i++) {
			returned7bitArray = Decoder7bit(tmp);
			s += '\ttune_time: ' + returned7bitArray[0] + '\n\t';
			tmp = tmp.substring(returned7bitArray[1], tmp.length);
			
			returned7bitArray = Decoder7bit(tmp);
			s += '\tduration: ' + returned7bitArray[0] + '\n\t';
			tmp = tmp.substring(returned7bitArray[1], tmp.length);
		}
		s = s.substring(0, s.length-1);
		
		return [s, tmp];
	}		
	
	function event9(msg) {
		var tmp = msg;
		var s = ' VOD Playing/Ordering\n\t';
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'vod_action: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'vod_asset_id: ' + returned7bitArray[0] + '\n\t';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'vod_context_id: ' + returned7bitArray[0] + '\n';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		return [s, tmp];
	}		

//	eventsParameters returns parsed parameters for some event_id as string and left unparsed string
	function eventsParameters(id, msg) {
		var s = '';
		var evParam;
		switch (id) {
			case 0: { evParam = event0(msg); break; }
			case 1: { evParam = event1(msg); break; }
			case 2: { evParam = event2(msg); break; }
			case 3: { evParam = event3(msg); break; }
			case 4: { evParam = event4(msg); break; }
			case 5: { evParam = event5(msg); break; }
			case 6: { evParam = event6(msg); break; }
			case 7: { evParam = event7(msg); break; }
			case 8: { evParam = event8(msg); break; }
			case 9: { evParam = event9(msg); break; }
			default: { evParam = [s, msg];  break; }
		}
		s = evParam[0];
		tmp = evParam[1];
		return [s, tmp];
	}

//	packagePart returns parsed parameters for one package as string and left unparsed string	
	function packagePart(msg) {
		var tmp = msg;
		var s = '';
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'packageType: ' + returned7bitArray[0] + '\n';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		s += 'study_code: ' + returned7bitArray[0] + '\n';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		s += 'start_timestamp: ' + getStartTimestamp(tmp) + '\n';
		tmp = tmp.substring(8, tmp.length);
		
		returned7bitArray = Decoder7bit(tmp);
		eventsNumber = returned7bitArray[0];
		s += 'events_number: ' + eventsNumber + '\n';
		tmp = tmp.substring(returned7bitArray[1], tmp.length);
		
		for (var i = 0; i < eventsNumber; i++) {
			returned7bitArray = Decoder7bit(tmp);
			s += 'time_delta: '+ returned7bitArray[0] + '\n';
			tmp = tmp.substring(returned7bitArray[1], tmp.length);
			
			returned7bitArray = Decoder7bit(tmp);
			var ev_id = returned7bitArray[0];
			s += 'event_ID: '+ ev_id;
			tmp = tmp.substring(returned7bitArray[1], tmp.length);
			
			returnedParameters = eventsParameters(ev_id, tmp);
			s += returnedParameters[0];
			tmp = returnedParameters[1];
		}
		
		return [s, tmp];
	}
	
	function addhandlers(f) {
		f.clearbutton.onclick = function() {
			this.form.dcMsg.value='';
			this.form.parsedMsg.value='';
		}
		f.parsebutton.onclick = function() {
			var Correctness = isMsgCorrect(this.form.dcMsg.value);
			var isCorrect = Correctness[0];
			var msg = Correctness[1];
			var s = msg;
			
			if (isCorrect) {
				s = '';
				var cP = commonPart(msg);
				s += cP[0];
				msg = cP[1];

				while (msg.length > 0) {
					pP = packagePart(msg);
					s += '\n' + pP[0];
					msg = pP[1];
				}
			}
			this.form.parsedMsg.value = s;			
		}
	}