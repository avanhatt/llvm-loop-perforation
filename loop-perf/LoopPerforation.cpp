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

      errs() << "I am a loop " << *L << "!\n";


      bool IsSimple = L->isLoopSimplifyForm();


      errs() << "Am I simple?  " << IsSimple << "!\n";

      if (!IsSimple) {
        // We don't modify unsimplified loops
        return false;
      }

      PHINode *PHI = L->getCanonicalInductionVariable();

      if (PHI != nullptr) {
        errs() << "Induction variable:  " << *PHI << "!\n";
      } else {
        errs() << "No induction variable!\n";
      }

      return false;
    }
  };
}

char LoopPerforationPass::ID = 0;

// Register the pass so `opt -loop-perf` runs it.
static RegisterPass<LoopPerforationPass> X("loop-perf", "loop perforation pass");
