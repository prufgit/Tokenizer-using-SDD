from fastapi import APIRouter

from app.schemas.bpe import BpeModelResponse, BpeTrainRequest
from app.services import bpe_service
from app.services.bpe_model_store import bpe_model_store

router = APIRouter()


def _to_response() -> BpeModelResponse:
    model = bpe_model_store.current()
    return BpeModelResponse(
        trained=model.trained,
        vocabulary=[{"id": tid, "token": tok} for tok, tid in model.vocabulary.items()],
        merge_rules=[
            {
                "order": rule.order,
                "left": rule.left,
                "right": rule.right,
                "merged": rule.merged,
                "merged_id": rule.merged_id,
            }
            for rule in model.merge_rules
        ],
        training_steps=[
            {"step": step.step, "pair_selected": step.pair_selected, "merged_into": step.merged_into}
            for step in model.training_steps
        ],
        target_vocab_size=model.target_vocab_size,
        achieved_vocab_size=model.achieved_vocab_size,
    )


@router.post("/api/bpe/train", response_model=BpeModelResponse)
def post_bpe_train(request: BpeTrainRequest) -> BpeModelResponse:
    model = bpe_service.train(request.training_text, request.target_vocab_size)
    bpe_model_store.replace(model)
    return _to_response()


@router.get("/api/bpe/model", response_model=BpeModelResponse)
def get_bpe_model() -> BpeModelResponse:
    return _to_response()
