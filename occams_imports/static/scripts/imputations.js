function choiceModel(name, label){
  'use strict'

  var self = this;

  self.name = ko.observable(name);
  self.label = ko.observable(label);
  self.mapped = ko.observable('');
}

function attributeModel(variable, label, choices){
  'use strict'

  var self = this;

  self.variable = ko.observable(variable);
  self.label = ko.observable(label);
  self.choices = ko.observableArray([]);

  var choicesLength = choices.length;

  for (var i = 0; i < choicesLength; i++){
    self.choices.push(new choiceModel(choices[i].name, choices[i].label));
  }
}

function formModel(name, publish_date, attributes){
  'use strict'

  var self = this;

  self.name = ko.observable(name);
  self.publish_date = ko.observable(publish_date);
  self.attributes = ko.observableArray([]);

  var attributeLength = attributes.length;

  for (var i = 0; i < attributeLength; i++){
    self.attributes.push(
      new attributeModel(
        attributes[i].variable, attributes[i].label, attributes[i].choices));
  }
}

function comparisonModel(){
  'use strict';

  var self = this;

  self.operators = ko.observableArray(['==', '!=', '>', '<', '>=', '<=']);
  self.selectedOperator = ko.observable();
  self.value = ko.observable();
}

comparisonModel.prototype.toJSON = function() {
  // remove unnecessary operators attribute to clean up
  // ko.JSON results
  'use strict'

  var self = this;

  var copy = ko.toJS(self);
  delete copy.operators;

  return copy;
}

function logicalModel(){
  'use strict'

  var self = this;

  self.operators = ko.observableArray(['and', 'or']);
  self.comparisons = ko.observableArray([]);
  self.selectedOperator = ko.observable();

  self.addComparisonOperator = function(){
    'use strict'

    var self = this;
    self.comparisons.push(new comparisonModel());
  }

  self.deleteComparisonOperator = function(){
    'use strict'

    var self = this;
    self.comparisons.pop()
  }
}

logicalModel.prototype.toJSON = function() {
  // remove unnecessary operators attribute to clean up
  // ko.JSON results
  'use strict'

  var self = this;

  var copy = ko.toJS(self);
  delete copy.operators;

  return copy;
}

function conversionModel(){
  'use strict'

  var self = this;

  self.mathOperators = ko.observableArray(['multiply', 'divide', 'add', 'subtract']);
  self.operatorChoices = ko.observableArray(['By variable', 'By value'])
  self.selectedOperator = ko.observable();
  self.selectedOperatorChoice = ko.observable();
  self.selectedForm = ko.observable();
  self.selectedAttribute = ko.observable();
  self.newConversion = ko.observable(false);
  self.value = ko.observable();
}

conversionModel.prototype.toJSON = function(){
  'use strict'

  var self = this;

  var copy = ko.toJS(self);
  delete copy.mathOperators;
  delete copy.selectedAttribute.label;
  delete copy.selectedAttribute.choices;

  if (copy.selectedForm !== undefined){
    delete copy.selectedForm.attributes;

  }
  return copy;
}

function bucketModel(){
  'use strict'

  var self = this;

  self.conversions = ko.observableArray([new conversionModel()]);
}

function imputationViewModel(){
  'use strict';

  var self = this;

  self.conditions = ko.observableArray(['any', 'all']);
  self.selectedComparisonCondition = ko.observable();
  self.comparisonOperators = ko.observableArray([]);
  self.logicalOperators = ko.observableArray([]);
  self.confidence = ko.observable(1);

  self.isReady = ko.observableArray(false);
  self.isLoading = ko.observable(true);

  self.forms = ko.observableArray();

  self.buckets = ko.observableArray();

  self.drsc_forms = ko.observableArray();
  self.selectedDRSCForm = ko.observable();
  self.selectedDRSCAttribute = ko.observable();
  self.selectedMapTo = ko.observable();

  self.conversionLabel = ko.observable();
  self.imputationLabel = ko.observable();

  self.isSuccess = ko.observable(false);
  self.isDanger = ko.observable(false);
  self.msgType = ko.observable('Info - ');
  self.msg = ko.observable('Please wait until form loading is complete.');
  self.isInfo = ko.observable(true);

  self.addLogicalOperator = function(){
    self.logicalOperators.push(new logicalModel());

  }

  self.addComparisonOperator = function(){
    'use strict'

    var self = this;

    self.comparisonOperators.push(new comparisonModel());
  }

  self.addConversion = function(bucket){
    'use strict'

    var self = this;

    bucket.conversions.push(new conversionModel());
  }

  self.addBucket = function(){
    'use strict'

    self.buckets.push(new bucketModel());
  }

  self.removeBucket = function(bucket){
    'use strict'

    self.buckets.remove(bucket);
  }

  self.deleteComparisonOperator = function(){
    'use strict'

    var self = this;

    self.comparisonOperators.pop()
  }

  self.deleteConversion = function(){
    'use strict'

    var self = this;

    self.conversions.pop()
  }

  self.deleteLogicalOperator = function(){
    'use strict'

    var self = this;

    self.logicalOperators.pop()
  }

  self.initOperatorAndValues = function(){
    //Sets values for operator and value to empty
    //if it's first element in a new conversion
      var lastConversion = false;
      ko.utils.arrayForEach(self.conversions(), function(conversion){

        if (lastConversion === true){
          //this means this is the first conversion in a new bucket
          //remove illogical operators and values
          conversion.value('');
          conversion.selectedOperator('');
          lastConversion = false;
        }

        //this means the next conversion will be the new conversion
        //in a new bucket
        //ideally this would update via the UI
        if (conversion.newConversion() === true){
          lastConversion = true;
        }
    });
  }

  self.saveImputation = function(){
    'use strict'

    var noForm = false;

    ko.utils.arrayForEach(self.buckets(), function(bucket){
      ko.utils.arrayForEach(bucket.conversions(), function(conversion){
        if (conversion.selectedForm() === undefined){
          noForm = true;
        }
      });
    });

    if (noForm === true){
      self.isInfo(false);
      self.msgType('Error - ');
      self.msg('Please select a form for every variable operation.');
      self.isDanger(true);
    }

    else if (self.selectedDRSCForm() === undefined){
      self.isInfo(false);
      self.msgType('Error - ');
      self.msg('Please select a DRSC form to apply imputation.');
      self.isDanger(true);

      return;
    }


    else {

      //self.initOperatorAndValues();

      var data = ko.toJSON({buckets: self.buckets(),
                            //get first conversion form to determine site on server
                            //this assumes all conversion are of the same site
                            site: self.buckets()[0].conversions()[0].selectedForm(),
                            maps_to: self.selectedMapTo(),
                            logical: self.logicalOperators(),
                            comparison: self.comparisonOperators(),
                            selected_comparison_condition: self.selectedComparisonCondition,
                            drsc: self.selectedDRSCForm(),
                            selected_drsc: self.selectedDRSCAttribute(),
                            confidence: self.confidence(),
                            conversion_label: self.conversionLabel(),
                            imputation_label: self.imputationLabel()
                            })

      //delete unnecessary data from the json
      data = JSON.parse(data);
      delete data.selected_drsc.choices;
      delete data.drsc.attributes;
      delete data.site.attributes;
      delete data.site.selectedAttribute;
      data = JSON.stringify(data);

      console.log(data);

/*      $.ajax({
        url: '/imports/mappings/imputation/map',
        method: 'POST',
        data: data,
        headers: {'X-CSRF-Token': $.cookie('csrf_token')},
        beforeSend: function(){
        },
        success: function(data, textStatus, jqXHR){
          window.location.href = '/imports';
        },
        complete: function(){
        }
      });*/
    }
  }

  //get initial form data
  $.ajax({
    url: '/imports/schemas',
    method: 'GET',
    headers: {'X-CSRF-Token': $.cookie('csrf_token')},
    beforeSend: function(){
      self.isReady(true);
      self.buckets.push(new bucketModel());
    },
    success: function(data, textStatus, jqXHR){
      var json = $.parseJSON(data);

      $.each(json.forms, function(){
        var form = new formModel(this.name, this.publish_date, this.attributes);
        if (this.site != 'DRSC'){
          self.forms.push(form);
        }
        else{
          self.drsc_forms.push(form);
        }
      });
    },
    complete: function(){
      self.isLoading(false);
  }
  });
}