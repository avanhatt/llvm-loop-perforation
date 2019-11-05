#include "llvm/Analysis/LoopInfo.h"
#include "llvm/Analysis/LoopPass.h"
#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/Transforms/Utils.h"
using namespace llvm;

namespace {
  struct LoopPerforationPass : public LoopPass {
    static char ID;
    LoopPerforationPass() : LoopPass(ID) {}

    void getAnalysisUsage(AnalysisUsage &AU) const {
      AU.addRequired<LoopInfoWrapperPass>();
      AU.addRequiredID(LoopSimplifyID);
    }


    virtual bool runOnLoop(Loop *L, LPPassManager &LPM) {

      errs() << "I am a loop called " << L->getName() << "!\n";


      bool isSimple = L->isLoopSimplifyForm();


      errs() << "Am I simple?  " << isSimple << "!\n";

      // LoopInfo &LI = getAnalysis<LoopInfoWrapperPass>().getLoopInfo();
      // LI.print(errs());

      return false;
    }
  };
}

char LoopPerforationPass::ID = 0;

// Register the pass so `opt -loop-perf` runs it.
static RegisterPass<LoopPerforationPass> X("loop-perf", "loop perforation pass");
