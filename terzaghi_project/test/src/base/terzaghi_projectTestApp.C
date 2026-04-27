//* This file is part of the MOOSE framework
//* https://www.mooseframework.org
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html
#include "terzaghi_projectTestApp.h"
#include "terzaghi_projectApp.h"
#include "Moose.h"
#include "AppFactory.h"
#include "MooseSyntax.h"

InputParameters
terzaghi_projectTestApp::validParams()
{
  InputParameters params = terzaghi_projectApp::validParams();
  params.set<bool>("use_legacy_material_output") = false;
  params.set<bool>("use_legacy_initial_residual_evaluation_behavior") = false;
  return params;
}

terzaghi_projectTestApp::terzaghi_projectTestApp(InputParameters parameters) : MooseApp(parameters)
{
  terzaghi_projectTestApp::registerAll(
      _factory, _action_factory, _syntax, getParam<bool>("allow_test_objects"));
}

terzaghi_projectTestApp::~terzaghi_projectTestApp() {}

void
terzaghi_projectTestApp::registerAll(Factory & f, ActionFactory & af, Syntax & s, bool use_test_objs)
{
  terzaghi_projectApp::registerAll(f, af, s);
  if (use_test_objs)
  {
    Registry::registerObjectsTo(f, {"terzaghi_projectTestApp"});
    Registry::registerActionsTo(af, {"terzaghi_projectTestApp"});
  }
}

void
terzaghi_projectTestApp::registerApps()
{
  registerApp(terzaghi_projectApp);
  registerApp(terzaghi_projectTestApp);
}

/***************************************************************************************************
 *********************** Dynamic Library Entry Points - DO NOT MODIFY ******************************
 **************************************************************************************************/
// External entry point for dynamic application loading
extern "C" void
terzaghi_projectTestApp__registerAll(Factory & f, ActionFactory & af, Syntax & s)
{
  terzaghi_projectTestApp::registerAll(f, af, s);
}
extern "C" void
terzaghi_projectTestApp__registerApps()
{
  terzaghi_projectTestApp::registerApps();
}
