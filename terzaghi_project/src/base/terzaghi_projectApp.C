#include "terzaghi_projectApp.h"
#include "Moose.h"
#include "AppFactory.h"
#include "ModulesApp.h"
#include "MooseSyntax.h"

InputParameters
terzaghi_projectApp::validParams()
{
  InputParameters params = MooseApp::validParams();
  params.set<bool>("use_legacy_material_output") = false;
  params.set<bool>("use_legacy_initial_residual_evaluation_behavior") = false;
  return params;
}

terzaghi_projectApp::terzaghi_projectApp(InputParameters parameters) : MooseApp(parameters)
{
  terzaghi_projectApp::registerAll(_factory, _action_factory, _syntax);
}

terzaghi_projectApp::~terzaghi_projectApp() {}

void
terzaghi_projectApp::registerAll(Factory & f, ActionFactory & af, Syntax & syntax)
{
  ModulesApp::registerAllObjects<terzaghi_projectApp>(f, af, syntax);
  Registry::registerObjectsTo(f, {"terzaghi_projectApp"});
  Registry::registerActionsTo(af, {"terzaghi_projectApp"});

  /* register custom execute flags, action syntax, etc. here */
}

void
terzaghi_projectApp::registerApps()
{
  registerApp(terzaghi_projectApp);
}

/***************************************************************************************************
 *********************** Dynamic Library Entry Points - DO NOT MODIFY ******************************
 **************************************************************************************************/
extern "C" void
terzaghi_projectApp__registerAll(Factory & f, ActionFactory & af, Syntax & s)
{
  terzaghi_projectApp::registerAll(f, af, s);
}
extern "C" void
terzaghi_projectApp__registerApps()
{
  terzaghi_projectApp::registerApps();
}
