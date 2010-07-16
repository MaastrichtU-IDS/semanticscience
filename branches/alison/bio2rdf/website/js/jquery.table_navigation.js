/**
 * Table navigation with keys v0.6.1 2007-08-30
 * 
 * Idea by Florian Seefried <florian.seefried@helionweb.de>.
 * Implemented by Stephan Soller <stephan.soller@addcom.de>.
 * 
 * Cookie handling functions form Quirks Mode written by Scott Andrew and edited
 * by Peter-Paul Koch (http://www.quirksmode.org/js/cookies.html).
 * getPos and getScroll functions are taken from the Interface Elements for jQuery
 * utility plugin by Stefan Petre (http://interface.eyecon.ro).
 * The first version of the on_activate option and the improved cookie_name option
 * were contributed by Roberto Rambaldi.
 */

/**
 * This is the jQuery namespace of this plugin used to store "global" values respectively
 * objects and values which have to exist after or outside the jQuery.tableNavigation()
 * function (defined after this namespace).
 */
jQuery.extendedNavigation = {
	settings: null,
	internal_event_hanlders: {},
	tables: []
};

/**
 * Usual configuration options
 * 
 * "table_selector" is the CSS selector used to get all elements (read tables) which
 * 	contains selectable rows. This is used to jump between multible tables and to
 * 	highlight the current table with the class specified in the "focused_table_class"
 * 	option.
 * "row_selector" is the CSS selector used to get all navigateable table rows.
 * "selected_class" is the name of the CSS class identifying the selected table row.
 * "activation_selector" is the CSS selector which is used to find the rows activation
 * 	element. This element will be focused when the row is selected. When a row is
 * 	activated and this element is a link the user will be redirected to it's target URI.
 * "bind_key_events_to_links" let you controll if the key press event should be bound
 * 	to the activation links of the rows (true) or to the document object (false). If
 * 	the events are bound to the document object forms on the same page will not
 * 	work properly but the script won't need the focus to work. Default value is true,
 * 	to get pre v0.5.4 behaviour set it to false.
 * "focus_links_on_select" specifies if the activation link should be focused when
 * 	selecting a row. This is neccessary for the key press events to work if the
 * 	"bind_key_events_to_links" option is set to false. Defaults to true  but if
 * 	you want pre v0.5.4 behaviour set it to false.
 * "select_event" is the event which will select the corresponding row. Usually it's
 * 	a mouse click ('click') but you can use all event names supported by jQuery
 * 	(see http://docs.jquery.com/Events).
 * "activate_event" is the event activating the currently selected row. You can use
 * 	all event names supported by jQuery (see http://docs.jquery.com/Events).
 * "activation_element_activate_event" is the event of the activation element which
 * 	activates the the currently selected row. You can use all event names supported
 * 	by jQuery (see http://docs.jquery.com/Events) or set it to false or null to not bind
 * 	any event to the activation element.
 * "scroll_overlap" is the amount of pixels that gets added to a scroll command
 * 	if the viewport must be scrolled to see a selected row. If the viewport
 * 	gets scrolled up to make an element visible the user sees the next X
 * 	pixels over the element, too.
 * "cookie_name" is the name of the cookie used to store the index of the last
 * 	activated row. This is used to select the same row if the user returns to
 * 	the table using the back button or key. Set this option to null to disable
 * 	cookies.
 * "focus_tables" is a switch (true or false) to toggle the highlighting of the current
 * 	table. If set to true the table of the currently selected row will be marked with
 * 	the class specified in the "focused_table_class" option. Set to false if you just
 * 	have one table on a page and/or to increase the performance of the script.
 * "focused_table_class" is the CSS class name used to highlight the table of the
 * 	currently selected table row.
 * "jump_between_tables" is a switch (true or false) which allows you to controll if the
 * 	script can jump between multiple tables on one page. If set to true and the last row
 * 	of a table is reached the next row selected will be the first row of the next table.
 * 	Note that this can confuse users because the keyborad focus and the view port also
 * 	jumps to the first row of the next table.
 * "disabled" is a switch (true or false) to temporarily disable all event
 * 	handlers used by the script. 
 * 
 * Configuration of user specified event handlers
 * 
 * User specified event handlers can be used to customize the behaviour of this
 * plugin to your needs. Before the script reacts to an event (like selecting a row)
 * it will execute the event handler you can specify here. For example this can be
 * used to update a part of the page with detailed information if the user selects
 * a new row.
 * 
 * An user specified event hanlder should be a function taking exactly one parameter:
 * the row affected by the event. You can also specify a string starting with "on". This
 * string will be interpreted as an attribute name of the affected row and the value of
 * the attribute will be evaled. If the string does not start with "on" it will be directly
 * evaled. For better coding practice and easier debugging a function is us more useful.
 * 
 * An event handler can return false to prevent the script from doings it's default
 * actions like highlighting the selected row and scrolling to it. This is useful if your
 * event handler already does all necessary stuff and don't want the script to interfer.
 * 
 * These events are currently available:
 * 
 * "on_select" is executed before a row gets selected. The scripts default action is to
 * 	highlight the row and scroll the page to make it visible (if neccessary).
 * "on_activate" is executed before a row gets activated. The default action is to
 * 	redirect the browser to the location of the rows activation link.
 */
jQuery.tableNavigation = function(settings) {
	// Check if the global table navigation settings are already defined. If not define default values and overwrite
	// them with the settings the user specified.
	// However if the global settings are already defined the tableNavigation() function was already called and all
	// event handler are already in place and registered through jQuery. To just continue and define all event
	// handlers again would lead to multiple registered event handlers and thus the same event would be processed
	// multiple times from different tableNavigation instances (keypress event will be process x times and therefore
	// the selected row will jump x rows for example). To avoid this we just update the global options and exit. The
	// already registered event handlers will use the updated global options from that on. If however the event handlers
	// should be missing (eg. on newly added elements) they will be bind by the bindInternalEventHandlers() function.
	// The bug leading to this code was reported by HT, thanks.
	if (jQuery.extendedNavigation.settings == null) {
		jQuery.extendedNavigation.settings = jQuery.extend({
			table_selector: 'table.navigateable',
			row_selector: 'table.navigateable tbody tr',
			selected_class: 'selected',
			activation_selector: 'a.activation',
			bind_key_events_to_links: true,
			focus_links_on_select: true,
			select_event: 'click',
			activate_event: 'dblclick',
			activation_element_activate_event: 'click',
			scroll_overlap: 20,
			cookie_name: 'last_selected_row_index',
			focus_tables: true,
			focused_table_class: 'focused',
			jump_between_tables: true,
			disabled: false,
			on_activate: null,
			on_select: null
		}, settings);
	} else {
		jQuery.extendedNavigation.settings = jQuery.extend(jQuery.extendedNavigation.settings, settings);
		jQuery.extendedNavigation.tables = jQuery(jQuery.extendedNavigation.settings.table_selector);
		bindInternalEventHandlers();
		return;
	}
	
	/**
	 * DOM initialization function, executed when the DOM is ready (page loading finished).
	 * Defines the event handlers and binds them to the current DOM tree.
	 */
	jQuery(document).ready(function() {
		defineInternalEventHandlers();
		jQuery.extendedNavigation.tables = jQuery(jQuery.extendedNavigation.settings.table_selector);
		bindInternalEventHandlers();
	});
	
	/**
	 * Defines the event handlers used by this script and stores them in the global
	 * jQuery.extendedNavigation.internal_event_hanlders object. This makes it possible to reuse the
	 * event handlers later on (eg. by the bindInternalEventHandlers() function when calling
	 * jQuery.tableNavigation() multiple times).
	 * 
	 * Defines functions to select a row on mouse click and to activate a row on double click as well as
	 * one for clicking on the activation links. A keypress function is also defined which reacts on three
	 * keys:
	 * - arrow down will select the next row of the table,
	 * - arrow up will select the previous row of the table,
	 * - enter will activate the currently selected row.
	 */
	function defineInternalEventHandlers() {
		jQuery.extendedNavigation.internal_event_hanlders.click = function(){
			if ( jQuery.extendedNavigation.settings.disabled ) { return }
			selectRow(this);
		};
		
		jQuery.extendedNavigation.internal_event_hanlders.dblclick = function(){
			if ( jQuery.extendedNavigation.settings.disabled ) { return }
			activateRow(this);
		};
		
		jQuery.extendedNavigation.internal_event_hanlders.activation_link_click = function(){
			if ( jQuery.extendedNavigation.settings.disabled ) { return }
			activateRow(jQuery(this).parents('tr').get(0));
			return false;
		};
		
		jQuery.extendedNavigation.internal_event_hanlders.activation_link_focus = function(){
			if ( jQuery.extendedNavigation.settings.disabled ) { return }
			selectRow(jQuery(this).parents('tr').get(0));
		};
		
		jQuery.extendedNavigation.internal_event_hanlders.keypress = function(e){
			if ( jQuery.extendedNavigation.settings.disabled ) { return }
			
			var key_code = e.keyCode;
			switch (key_code){
				case 40: // arrow down
				case 39: // arrow right
					var next_row = getSelectedRow().next();
					if (next_row.length > 0) {
						// selectRow returns true if the next row was selected. In this case we does not want
						// the arrow keys to cause a page scroll because the script handles the scrolling. However
						// if there is no next row to select (selectRow() returns false) we want to use the default
						// page scrolling. Because of this we simply invert the returned value of selectRow() and have
						// the behaviour we want.
						var r = !selectRow(next_row.get(0));
						return r;
					} else if ( jQuery.extendedNavigation.settings.jump_between_tables ) {
						var current_table = getSelectedRow().parents(jQuery.extendedNavigation.settings.table_selector).get(0);
						var all_tables = jQuery.extendedNavigation.tables;
						var next_row = undefined;
						all_tables.each(function(index){
							if ( this == current_table ) {
								var next_table = all_tables.eq(index + 1);
								if ( next_table != undefined ) { next_row = next_table.find('tbody tr:first') };
							}
						});
						return !selectRow(next_row.get(0));
					}
					break;
				case 38: // arrow up
				case 37: // arrow left
					var prev_row = getSelectedRow().prev();
					if (prev_row.length > 0) {
						// See the big comment block above for an explaination of this "return" line and it's
						// exclamation mark.
						var r = !selectRow(prev_row.get(0));
						return r;
					} else if ( jQuery.extendedNavigation.settings.jump_between_tables ) {
						var current_table = getSelectedRow().parents(jQuery.extendedNavigation.settings.table_selector).get(0);
						var all_tables = jQuery.extendedNavigation.tables;
						var prev_row = null;
						all_tables.each(function(index){
							if ( this == current_table ) {
								var prev_table = all_tables.eq(index - 1);
								if ( prev_table != undefined ) { prev_row = prev_table.find('tbody tr:last') };
							}
						});
						return !selectRow(prev_row.get(0));
					}
					break;
				case 13: // return
					activateRow(getSelectedRow().get(0));
					break;
			}
		};
	};
	
	/**
	 * Binds the event handlers defined by the defineInternalEventHandlers() function to the
	 * currently existing elements in the DOM tree. If no row is selected by the source code this
	 * function will selecte the last row read from the cookie or if no index was stored in a cookie
	 * the first row.
	 * 
	 * One special note about MSIE: For MSIE the keypress handler will be bound to the keydown
	 * event because keypress won't work for some reason.
	 * 
	 * This method is handy to restore the table navigation behavior if the DOM tree has changed
	 * (added or removed table rows).
	 */
	function bindInternalEventHandlers() {
		var selectable_rows = jQuery(jQuery.extendedNavigation.settings.row_selector);
		var selected_row = selectable_rows.filter("." + jQuery.extendedNavigation.settings.selected_class);
		
		if (selected_row.size() == 0 && selectable_rows.size() > 0){
			var index_to_select = readLastRowIndex();
			if (!index_to_select) {
				eraseLastRowIndexCookie();
				index_to_select = 0;
			}
			var row_to_select = selectable_rows.get(index_to_select);
			if (row_to_select) {selectRow(row_to_select);}
		}
		
		selectable_rows.bind(jQuery.extendedNavigation.settings.select_event, {}, jQuery.extendedNavigation.internal_event_hanlders.click);
		selectable_rows.bind(jQuery.extendedNavigation.settings.activate_event, {}, jQuery.extendedNavigation.internal_event_hanlders.dblclick);
		
		var activation_element = selectable_rows.find(jQuery.extendedNavigation.settings.activation_selector);
		if ( activation_element && jQuery.extendedNavigation.settings.activation_element_activate_event ) {
			selectable_rows.find(jQuery.extendedNavigation.settings.activation_selector).bind(jQuery.extendedNavigation.settings.activation_element_activate_event, {}, jQuery.extendedNavigation.internal_event_hanlders.activation_link_click);
		}
		activation_element.focus(jQuery.extendedNavigation.internal_event_hanlders.activation_link_focus);
		
		if (jQuery.extendedNavigation.settings.bind_key_events_to_links) {
			var bind_to = jQuery.extendedNavigation.settings.row_selector + ' ' + jQuery.extendedNavigation.settings.activation_selector;
		} else {
			var bind_to = document;
		}
		
		
		if (jQuery.browser.msie) {
			jQuery(bind_to).keydown(jQuery.extendedNavigation.internal_event_hanlders.keypress);
		} else {
			jQuery(bind_to).keypress(jQuery.extendedNavigation.internal_event_hanlders.keypress);
		}
	};
	
	/**
	 * Selects the specified row.
	 * 
	 * The "row" parameter is the DOM object of the TR tag that should be selected.
	 * Checks if the specified row is a TR tag because we don't want to select a tag that
	 * isn't a table row (like every tag that comes after or before the table).
	 * 
	 * Before selecting the row the user specified on_select event handler will be
	 * executed. See "jQuery.extendedNavigation.settings.on_select" configuration option.
	 * If this event handler returns false the script will not select the row assuming the
	 * user specified event handler does someting similar and do not want the script to
	 * interfer.
	 * 
	 * Returns false if there is no row to select otherwise true.
	 */
	function selectRow(row) {
		if (row != undefined && row.nodeName.toLowerCase() == "tr"){
			var do_default_action = executeEventHandler(row, jQuery.extendedNavigation.settings.on_select);
			
			if (do_default_action)
			{
				getSelectedRow().removeClass(jQuery.extendedNavigation.settings.selected_class);
				jQuery(row).addClass(jQuery.extendedNavigation.settings.selected_class);
				
				if (jQuery.extendedNavigation.settings.focus_links_on_select) {
					var activation_element = jQuery(row).find(jQuery.extendedNavigation.settings.activation_selector)[0];
					if (activation_element != null) {
						activation_element.focus();
					}
				}
				
				if (jQuery.extendedNavigation.settings.focus_tables) {
					jQuery.extendedNavigation.tables.removeClass(jQuery.extendedNavigation.settings.focused_table_class);
					jQuery(row).parents(jQuery.extendedNavigation.settings.table_selector).eq(0).addClass(jQuery.extendedNavigation.settings.focused_table_class);
				}
				
				scrollToIfNeccessary(row);
			}
			return true;
		}
		return false;
	};
	
	/**
	 * Returns a jQuery object containing the currently selected row.
	 * 
	 * The selected row is found by concatinating the row_selector setting with a point and
	 * the selected_class setting. This produces a selector like "...tr.selected" which should
	 * match the selected row.
	 */
	function getSelectedRow() {
		return jQuery(jQuery.extendedNavigation.settings.row_selector + "." + jQuery.extendedNavigation.settings.selected_class);
	}
	
	/**
	 * Activates a table row.
	 * 
	 * Activate means four things:
	 * - The specified table row will be selected (see selectRow function above).
	 * - The index of the activated row will be stored in a cookie unless
	 *   "jQuery.extendedNavigation.settings.cookie_name" is not null.
	 * - If present the user specified on_activate event handler will be
	 *   executed. See "jQuery.extendedNavigation.settings.on_activate" or the
	 *   docs of the configuration at the beginning of the file for more detaild
	 *   information. If the event handler returns false the next step will be skipped.
	 * - Finaly the browser will be redirected to the locaton this rows activation
	 *   link points to. This is the value of the "href" attribute of the first
	 *   element selected by the "jQuery.extendedNavigation.settings.activation_selector"
	 *   option (see begin of file).
	 */
	function activateRow(row) {
		if (row != undefined) {
			selectRow(row);
			
			var activated_index = jQuery(jQuery.extendedNavigation.settings.row_selector).index(row);
			storeLastRowIndex(activated_index);
			
			var do_default_action = executeEventHandler(row, jQuery.extendedNavigation.settings.on_activate);
			
			if (do_default_action)
			{
				var activation_link = jQuery(jQuery.extendedNavigation.settings.activation_selector, row);
				if (activation_link.size() == 1) {
					var href_of_activation_link = activation_link.attr("href");
					if ( href_of_activation_link != undefined ) {
						window.location.href = href_of_activation_link;
					}
				}
			}
		}
	};
	
	
	/**
	 * Executes an user defined event handler.
	 * 
	 * This function is the central place where user defined event handlers (values of
	 * the on_select and on_activate options, supplied as the action parameter) gets
	 * executed.
	 * 
	 * If the user supplied a function it will be called with the corresponding
	 * row as the first and only parameter. If the user defined action is a string
	 * and starts with "on" (eg. "onclick") it will be interpreted as a attribute name.
	 * The value of this attribute will be evaled. Any other string will will be evaled
	 * as JavaScript code.
	 * 
	 * The return value of the function specifies if the default action of the
	 * corresponding event should be done (true) or if it should be skipped (false).
	 */
	function executeEventHandler(row, action) {
		if (typeof action == "function")
		{
			return action(row);
		}
		else if (/^on/.test(action))
		{
			try {
				var onclick_of_target_link = jQuery(jQuery.extendedNavigation.settings.activation_selector, row).attr(action);
				if (eval(onclick_of_target_link) == false) {
					return false;
				} else {
					return true;
				}
			} catch(e) {
				return true;
			}
		}
		else if (typeof action == "string")
		{
			try {
				if (eval(action) == false) {
					return false;
				} else {
					return true;
				}
			} catch(e) {
				return true;
			}
		}
		
		return true;
	}
	
	/**
	 * This one is a little bit of a monster.
	 * 
	 * If neccessary it scrolls the viewport to make the specified element visible.
	 * This function uses the utility functions of Interface Elements for jQuery
	 * (http://interface.eyecon.ro) by Stefan Petre.
	 * 
	 * The scroll calculations are documented inside the function.
	 */
	function scrollToIfNeccessary(e) {
		var viewport_dimensions = getScroll();
		var viewport = {
			top: viewport_dimensions.t,
			left: viewport_dimensions.l,
			height: viewport_dimensions.ih,
			width: viewport_dimensions.iw
		};
		var element_position = getPos(e);
		
		var calculated_boundaries = {
			top: element_position.y - jQuery.extendedNavigation.settings.scroll_overlap,
			bottom: element_position.y + element_position.hb + jQuery.extendedNavigation.settings.scroll_overlap,
			left: element_position.x - jQuery.extendedNavigation.settings.scroll_overlap,
			right: element_position.x + element_position.wb + jQuery.extendedNavigation.settings.scroll_overlap
		};
		
		// These variables hold the final coordinates to scroll to. Default values
		// are the current coordinages of the viewport which will result in no
		// scrolling at all.
		var scroll_to_x = viewport.left;
		var scroll_to_y = viewport.top;
		
		// If the elements bottom line is below the viewports bottom line
		// scroll to the elements bottom line - the viewprots height. This way
		// the element is shown at the bottom of the screen.
		if (viewport.top + viewport.height < calculated_boundaries.bottom){scroll_to_y = calculated_boundaries.bottom - viewport.height;}
		
		// If the elements top line is over of the viewports top line scroll to
		// the elements top line so it's completely in view.
		if (viewport.top > calculated_boundaries.top){scroll_to_y = calculated_boundaries.top;}
		
		// If the _left_ border line of the element is greater than the right
		// border line of the viewport (element out to the right side) scroll
		// to the right border line of the element minus the width of the viewport.
		// This way the element is visible at the right side of the viewport.
		if (viewport.left + viewport.width < calculated_boundaries.left){scroll_to_x = calculated_boundaries.right - viewport.width;}
		
		// If the left border line of the element is smaller than the left
		// border line of the viewport scroll to the left border line of the
		// element.
		if (viewport.left > calculated_boundaries.left){scroll_to_x = calculated_boundaries.left}
		
		window.scrollTo(scroll_to_x, scroll_to_y);
	};
	
	/**
	 * This little function will read the index of the last activated row.
	 * 
	 * The value is stored in a cookie. The function will also check if the URL in
	 * the cookie is the same as the current one. If so the stored index will be
	 * returned. If the URLs don't match or no cookie exists null will be returned.
	 */
	function readLastRowIndex() {
		if (jQuery.extendedNavigation.settings.cookie_name)
		{
			var data = readCookie(jQuery.extendedNavigation.settings.cookie_name);
			if (data) {
				var data_elements = data.split(",");
				var last_index = data_elements[0];
				var last_href = data_elements[1];
				if (window.location.href == last_href) {
					return last_index;
				}
			}
		}
		return null;
	};
	
	/**
	 * Function to store the index of the activated row to use it in subsequent requests.
	 * 
	 * Stores the specified index and the current URL in a cookie. This cookie will
	 * used later on by the readLastRowIndex() function to get the last activated
	 * index.
	 */
	function storeLastRowIndex(index) {
		if (jQuery.extendedNavigation.settings.cookie_name)
		{
			var data = "" + index +"," + window.location.href;
			createCookie(jQuery.extendedNavigation.settings.cookie_name, data);
 		}
	};
	
	/**
	 * Function to erase the cookie storing the last activated row index.
	 */
	function eraseLastRowIndexCookie() {
		eraseCookie(jQuery.extendedNavigation.settings.cookie_name);
	};
	
	
	/**
	 * Cookie handling functions form Quirks Mode written by Scott Andrew and edited
	 * by Peter-Paul Koch (http://www.quirksmode.org/js/cookies.html).
	 */
	
	function createCookie(name,value,days) {
		if (days) {
			var date = new Date();
			date.setTime(date.getTime()+(days*24*60*60*1000));
			var expires = "; expires="+date.toGMTString();
		}
		else var expires = "";
		document.cookie = name+"="+value+expires+"; path=/";
	};
	
	function readCookie(name) {
		var nameEQ = name + "=";
		var ca = document.cookie.split(';');
		for(var i=0;i < ca.length;i++) {
			var c = ca[i];
			while (c.charAt(0)==' ') c = c.substring(1,c.length);
			if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
		}
		return null;
	}
	
	function eraseCookie(name) {
		createCookie(name,"",-1);
	};
	
	
	/**
	 * Functions of the Interface Elements for jQuery utility plugin by Stefan Petre
	 * http://interface.eyecon.ro
	 */
	
	function getPos(e, s)
	{
		var l = 0;
		var t  = 0;
		var sl = 0;
		var st  = 0;
		var w = jQuery.css(e,'width');
		var h = jQuery.css(e,'height');
		var wb = e.offsetWidth;
		var hb = e.offsetHeight;
		while (e.offsetParent){
			l += e.offsetLeft + (e.currentStyle?parseInt(e.currentStyle.borderLeftWidth)||0:0);
			t += e.offsetTop  + (e.currentStyle?parseInt(e.currentStyle.borderTopWidth)||0:0);
			if (s) {
				sl += e.parentNode.scrollLeft||0;
				st += e.parentNode.scrollTop||0;
			}
			e = e.offsetParent;
		}
		l += e.offsetLeft + (e.currentStyle?parseInt(e.currentStyle.borderLeftWidth)||0:0);
		t += e.offsetTop  + (e.currentStyle?parseInt(e.currentStyle.borderTopWidth)||0:0);
		st = t - st;
		sl = l - sl;
		return {x:l, y:t, sx:sl, sy:st, w:w, h:h, wb:wb, hb:hb};
	}
	
	function getScroll(e) 
	{
		if (e) {
			t = e.scrollTop;
			l = e.scrollLeft;
			w = e.scrollWidth;
			h = e.scrollHeight;
			iw = 0;
			ih = 0;
		} else  {
			if (document.documentElement && document.documentElement.scrollTop) {
				t = document.documentElement.scrollTop;
				l = document.documentElement.scrollLeft;
				w = document.documentElement.scrollWidth;
				h = document.documentElement.scrollHeight;
			} else if (document.body) {
				t = document.body.scrollTop;
				l = document.body.scrollLeft;
				w = document.body.scrollWidth;
				h = document.body.scrollHeight;
			}
			iw = self.innerWidth||document.documentElement.clientWidth||document.body.clientWidth||0;
			ih = self.innerHeight||document.documentElement.clientHeight||document.body.clientHeight||0;
		}
		return { t: t, l: l, w: w, h: h, iw: iw, ih: ih };
	}
};
