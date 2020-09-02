$(document).ready(function(){

	element = $("#cy");
	var explorer;

	function Graph(container) {

		this.cy = cytoscape({
			// very commonly used options
			container: container,
			elements: [ ],
			style: [ 
				{
					selector: 'node',
					style: {
						'background-color': '#00B4D8',
						'label': 'data(id)',
						'width': 'data(weight)',
						'height': 'data(weight)',
					}
				},
				{
					selector: 'edge',
					style: {
						'width': 3,
						'line-color': '#ccc',
						'target-arrow-color': '#ccc',
						'target-arrow-shape': 'triangle',
						'curve-style': 'bezier',
						'color': '#a33',
						'label': 'data(name)'
					}
				}
    		],
			layout: {
				name: 'cose',
				idealEdgeLength: 100,
				nodeOverlap: 20,
				refresh: 20,
				fit: true,
				padding: 30,
				randomize: true,
				componentSpacing: 100,
				nodeRepulsion: 400000,
				edgeElasticity: 100,
				nestingFactor: 5,
				gravity: 80,
				numIter: 1000,
				initialTemp: 200,
				coolingFactor: 0.95,
				minTemp: 1.0
			},

			// initial viewport state:
			zoom: 1,
			pan: { x: 0, y: 0 },

			// interaction options:
			minZoom: 1e-50,
			maxZoom: 1e50,
			zoomingEnabled: true,
			userZoomingEnabled: true,
			panningEnabled: true,
			userPanningEnabled: true,
			boxSelectionEnabled: true,
			selectionType: 'single',
			touchTapThreshold: 8,
			desktopTapThreshold: 4,
			autolock: false,
			autoungrabify: false,
			autounselectify: false,

			// rendering options:
			headless: false,
			styleEnabled: true,
			hideEdgesOnViewport: false,
			textureOnViewport: false,
			motionBlur: false,
			motionBlurOpacity: 0.2,
			wheelSensitivity: 1,
			pixelRatio: 'auto'
			
		});

	}

	Graph.prototype.addNode = function(id,weight,x,y) {
		cy = this.cy;
		if(!cy.$id(id).length) {
			cy.add({
				group: 'nodes',
				data: { id:id, weight: Math.log(weight)*50 }
				//position: {x:x, y:y}
			});
		}
	};

	Graph.prototype.addEdge = function(id,weight,name,source,target) {
		cy = this.cy;
		if(!cy.$id(id).length) {
			cy.add({
				group: 'edges',
				data: { id:id, name:name, weight:weight, source:source, target:target }
			});
		}
	};

	Graph.prototype.explore = function (subject,weight) {
		var self = this;
		var cy = self.cy;
		$.get("/graph?subject="+subject+"&objects=5&branches=5",function(res,status,all){
			if(status=="success") {
				element.show();
				cy.$("*").remove();
				self.addNode(subject,weight,600,400);
				for(var i=0;i<res[0].relationships.length;i++) {
					var predicate = res[0].relationships[i];
					for(var j=0;j<predicate.relationships.length;j++) {
						var object = predicate.relationships[j];
						self.addNode(object.label,object.weight,i,j)
						self.addEdge(subject+'::'+predicate.label+'::'+object.label,predicate.weight,predicate.label,subject,object.label)
					}
				}
				
				//cy.fit(1200);
				var layout = cy.layout({
					name: 'cose',
					idealEdgeLength: 100,
					nodeOverlap: 20,
					refresh: 20,
					fit: true,
					padding: 30,
					randomize: false,
					componentSpacing: 100,
					nodeRepulsion: 4000000,
					edgeElasticity: 100,
					nestingFactor: 5,
					gravity: 80,
					numIter: 1000,
					initialTemp: 200,
					coolingFactor: 0.95,
					minTemp: 1.0
				});
				layout.run();
				
				//console.log(res);
			} else {
				console.log("Nope!",subject,weight)
			}
		});
	};

	// ------------------------------------------------

	function summarizeCore(core) {

		//Get the summary info
		$.get('/cores/'+core,function(res,status) {
			if (status=="success") {
				c = $('#concepts')
				p = $('#predicates')
				c.html('');
				p.html('');
				for(var i=0;i<res.concepts.length;i++){
					l = res.concepts[i].label
					w = res.concepts[i].count
					c.append(`<li data-label="${l}" data-count="${w}">${l} (${w})</li>`);
				}
				for(var i=0;i<res.predicates.length;i++){
					l = res.predicates[i].label
					w = res.predicates[i].count
					p.append(`<li data-label="${l}" data-count="${w}">${l} (${w})</li>`);
				}

				c.on('click','li',function(e){
					el = $(this);
					explorer.explore(el.attr('data-label'),parseInt(el.attr('data-count')));
				});
			}

		});

	}

	function swapCore() {
		option = $("#cores option:selected").first();
		if(!option) {
			option = $("#cores option").first();
		}
		core = encodeURI(option.val());
		//Change the core for querying
		$.post('/cores/'+core,function(res,status) {
			if (status=="success") {
				element.hide();
				console.log('Core changed to',core)
				summarizeCore(core)
			}
			
		})

	}

	// ------------------------------------------------

	$.get('/cores',function(res,status) {
		select = $("#cores");
		if (status=="success") {
			for(var i=0;i<res.cores.length;i++) {
				core = res.cores[i]
				option = $("<option value=\""+core+"\">"+core+"</option>");
				option.click()
				select.append(option)
			}
		}
		select.on("change",swapCore)
		swapCore();
	});

	// ------------------------------------------------

	$('#autocomplete').autocomplete({
	    serviceUrl: '/suggest',
	    transformResult: function(response) {
	    	response = JSON.parse(response)
		    return {
		        "suggestions": $.map(response.suggestions, function(dataItem) {
		            return { "value": dataItem.term, "data": dataItem.weight };
		        })
		    };
		},
	    onSelect: function (suggestion) {
	        explorer.explore(suggestion.value,suggestion.data);
	        //alert('You selected: ' + suggestion.value + ', ' + suggestion.data);
	    }
	});

	explorer = new Graph(element);

});